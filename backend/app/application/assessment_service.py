import uuid

from app.application.quality_score import compute_quality_score
from app.domain.assessment import (
    Assessment,
    AssessmentNotFoundError,
    AssessmentRepository,
    AssessmentStatus,
)
from app.domain.finding import Finding, FindingRepository, Severity
from app.domain.project import ProjectNotFoundError, ProjectRepository
from app.infrastructure import evidence_store
from app.infrastructure.scanners.git_client import clone_repository
from app.infrastructure.scanners.pytest_runner import PytestResult
from app.infrastructure.scanners.pytest_runner import run as run_pytest
from app.infrastructure.scanners.ruff_runner import RuffResult
from app.infrastructure.scanners.ruff_runner import run as run_ruff

_COVERAGE_WARNING_THRESHOLD = 70.0


def _ruff_findings(assessment_id: str, ruff_result: RuffResult) -> list[Finding]:
    findings: list[Finding] = []
    for violation in ruff_result.violations:
        severity = Severity.MEDIUM if violation.code.startswith(("E", "F")) else Severity.LOW
        findings.append(
            Finding(
                id=str(uuid.uuid4()),
                assessment_id=assessment_id,
                tool="ruff",
                severity=severity,
                category="quality",
                description=(
                    f"{violation.code}: {violation.message} "
                    f"({violation.filename}:{violation.line})"
                ),
            )
        )
    return findings


def _pytest_findings(assessment_id: str, pytest_result: PytestResult) -> list[Finding]:
    findings = [
        Finding(
            id=str(uuid.uuid4()),
            assessment_id=assessment_id,
            tool="pytest",
            severity=Severity.HIGH,
            category="tests",
            description=f"failing test: {node_id}",
        )
        for node_id in pytest_result.failed_tests
    ]
    findings.append(
        Finding(
            id=str(uuid.uuid4()),
            assessment_id=assessment_id,
            tool="pytest",
            severity=Severity.INFO,
            category="tests",
            description=f"{pytest_result.passed}/{pytest_result.total} tests passed",
        )
    )
    coverage_severity = (
        Severity.MEDIUM
        if pytest_result.coverage_percent < _COVERAGE_WARNING_THRESHOLD
        else Severity.INFO
    )
    findings.append(
        Finding(
            id=str(uuid.uuid4()),
            assessment_id=assessment_id,
            tool="coverage",
            severity=coverage_severity,
            category="quality",
            description=f"coverage: {pytest_result.coverage_percent}%",
        )
    )
    return findings


class AssessmentService:
    def __init__(
        self,
        assessment_repository: AssessmentRepository,
        finding_repository: FindingRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._assessments = assessment_repository
        self._findings = finding_repository
        self._projects = project_repository

    def run(self, project_id: str, version: str | None) -> Assessment:
        project = self._projects.get(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)

        assessment = self._assessments.create(project_id, version or "default")

        try:
            with clone_repository(project.repository_url, version) as cloned:
                resolved_version = f"{version or 'default'}@{cloned.resolved_ref}"
                self._assessments.update(
                    assessment.id, version=resolved_version, status=AssessmentStatus.RUNNING
                )

                pytest_result = run_pytest(cloned.path)
                ruff_result = run_ruff(cloned.path)

            evidence_store.save(assessment.id, "pytest", pytest_result.raw_report)
            evidence_store.save(assessment.id, "coverage", pytest_result.raw_coverage)
            evidence_store.save(assessment.id, "ruff", ruff_result.raw_report)

            findings = _pytest_findings(assessment.id, pytest_result) + _ruff_findings(
                assessment.id, ruff_result
            )
            self._findings.bulk_create(findings)

            quality_score = compute_quality_score(
                coverage_percent=pytest_result.coverage_percent,
                pytest_passed=pytest_result.passed,
                pytest_total=pytest_result.total,
                ruff_violations=ruff_result.violations,
            )

            updated = self._assessments.update(
                assessment.id,
                status=AssessmentStatus.COMPLETED,
                quality_score=quality_score,
            )
            assert updated is not None
            return updated

        except Exception as exc:  # noqa: BLE001 - scan failure is a domain outcome, not an API error
            self._findings.bulk_create(
                [
                    Finding(
                        id=str(uuid.uuid4()),
                        assessment_id=assessment.id,
                        tool="assessment",
                        severity=Severity.CRITICAL,
                        category="execution",
                        description=f"assessment failed: {exc}",
                    )
                ]
            )
            updated = self._assessments.update(assessment.id, status=AssessmentStatus.FAILED)
            assert updated is not None
            return updated

    def get(self, assessment_id: str) -> Assessment:
        assessment = self._assessments.get(assessment_id)
        if assessment is None:
            raise AssessmentNotFoundError(assessment_id)
        return assessment

    def list_for_project(self, project_id: str) -> list[Assessment]:
        return self._assessments.list_for_project(project_id)

    def list_findings(self, assessment_id: str) -> list[Finding]:
        return self._findings.list_for_assessment(assessment_id)
