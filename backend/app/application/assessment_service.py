import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Protocol, TypeVar

from app.application.quality_score import compute_quality_score
from app.application.security_score import compute_security_score
from app.domain.assessment import (
    Assessment,
    AssessmentNotFoundError,
    AssessmentRepository,
    AssessmentStatus,
)
from app.domain.finding import Finding, FindingRepository, Severity
from app.domain.project import ProjectNotFoundError, ProjectRepository
from app.infrastructure import evidence_store
from app.infrastructure.scanners.bandit_runner import BanditResult
from app.infrastructure.scanners.bandit_runner import run as run_bandit
from app.infrastructure.scanners.git_client import clone_repository
from app.infrastructure.scanners.gitleaks_runner import GitleaksResult
from app.infrastructure.scanners.gitleaks_runner import run as run_gitleaks
from app.infrastructure.scanners.pytest_runner import PytestResult
from app.infrastructure.scanners.pytest_runner import run as run_pytest
from app.infrastructure.scanners.ruff_runner import RuffResult
from app.infrastructure.scanners.ruff_runner import run as run_ruff
from app.infrastructure.scanners.semgrep_runner import SemgrepResult
from app.infrastructure.scanners.semgrep_runner import run as run_semgrep
from app.infrastructure.scanners.trivy_runner import TrivyResult
from app.infrastructure.scanners.trivy_runner import run as run_trivy

_COVERAGE_WARNING_THRESHOLD = 70.0
_SECURITY_CATEGORIES = {"security", "secrets", "misconfig"}
_SEVERITY_BY_VALUE = {severity.value: severity for severity in Severity}
_SEMGREP_SEVERITY_MAP = {"ERROR": Severity.HIGH, "WARNING": Severity.MEDIUM, "INFO": Severity.LOW}


def _safe_severity(value: str, default: Severity) -> Severity:
    return _SEVERITY_BY_VALUE.get(value.upper(), default)


def _tool_error_finding(assessment_id: str, tool: str, exc: Exception) -> Finding:
    return Finding(
        id=str(uuid.uuid4()),
        assessment_id=assessment_id,
        tool=tool,
        severity=Severity.CRITICAL,
        category="execution",
        description=f"scanner error: {exc}",
    )


class _ScanResult(Protocol):
    raw_report: str


T = TypeVar("T", bound=_ScanResult)


def _run_tool(
    assessment_id: str,
    tool: str,
    repo_path: Path,
    scan: Callable[[Path], T],
    build_findings: Callable[[str, T], list[Finding]],
) -> tuple[list[Finding], T | None]:
    """Runs one scanner in isolation: a failure here never aborts the whole assessment."""
    try:
        result = scan(repo_path)
    except Exception as exc:  # noqa: BLE001 - isolate this tool's failure from the others
        return [_tool_error_finding(assessment_id, tool, exc)], None
    evidence_store.save(assessment_id, tool, result.raw_report)
    return build_findings(assessment_id, result), result


def _ruff_findings(assessment_id: str, result: RuffResult) -> list[Finding]:
    findings: list[Finding] = []
    for violation in result.violations:
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


def _bandit_findings(assessment_id: str, result: BanditResult) -> list[Finding]:
    return [
        Finding(
            id=str(uuid.uuid4()),
            assessment_id=assessment_id,
            tool="bandit",
            severity=_safe_severity(issue.severity, Severity.MEDIUM),
            category="security",
            description=f"{issue.test_id}: {issue.message} ({issue.filename}:{issue.line})",
        )
        for issue in result.issues
    ]


def _semgrep_findings(assessment_id: str, result: SemgrepResult) -> list[Finding]:
    return [
        Finding(
            id=str(uuid.uuid4()),
            assessment_id=assessment_id,
            tool="semgrep",
            severity=_SEMGREP_SEVERITY_MAP.get(finding.severity, Severity.MEDIUM),
            category="security",
            description=(
                f"{finding.check_id}: {finding.message} ({finding.filename}:{finding.line})"
            ),
        )
        for finding in result.findings
    ]


def _gitleaks_findings(assessment_id: str, result: GitleaksResult) -> list[Finding]:
    return [
        Finding(
            id=str(uuid.uuid4()),
            assessment_id=assessment_id,
            tool="gitleaks",
            severity=Severity.CRITICAL,
            category="secrets",
            description=(
                f"{secret.rule_id}: {secret.description} ({secret.filename}:{secret.line})"
            ),
        )
        for secret in result.secrets
    ]


def _trivy_findings(assessment_id: str, result: TrivyResult) -> list[Finding]:
    return [
        Finding(
            id=str(uuid.uuid4()),
            assessment_id=assessment_id,
            tool="trivy",
            severity=_safe_severity(finding.severity, Severity.MEDIUM),
            category="secrets" if finding.kind == "secret" else "misconfig",
            description=f"{finding.rule_id}: {finding.message} ({finding.filename})",
        )
        for finding in result.findings
    ]


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
        all_findings: list[Finding] = []

        try:
            with clone_repository(project.repository_url, version) as cloned:
                resolved_version = f"{version or 'default'}@{cloned.resolved_ref}"
                self._assessments.update(
                    assessment.id, version=resolved_version, status=AssessmentStatus.RUNNING
                )
                repo_path = cloned.path

                # pytest + coverage: special-cased, needs raw numbers for the quality score
                # (not just findings) and writes two evidence files from one run.
                coverage_percent, pytest_passed, pytest_total = 0.0, 0, 0
                try:
                    pytest_result = run_pytest(repo_path)
                    evidence_store.save(assessment.id, "pytest", pytest_result.raw_report)
                    evidence_store.save(assessment.id, "coverage", pytest_result.raw_coverage)
                    all_findings += _pytest_findings(assessment.id, pytest_result)
                    coverage_percent = pytest_result.coverage_percent
                    pytest_passed = pytest_result.passed
                    pytest_total = pytest_result.total
                except Exception as exc:  # noqa: BLE001 - isolate from the other tools
                    all_findings.append(_tool_error_finding(assessment.id, "pytest", exc))

                ruff_findings, ruff_result = _run_tool(
                    assessment.id, "ruff", repo_path, run_ruff, _ruff_findings
                )
                all_findings += ruff_findings

                quality_score = compute_quality_score(
                    coverage_percent=coverage_percent,
                    pytest_passed=pytest_passed,
                    pytest_total=pytest_total,
                    ruff_violations=ruff_result.violations if ruff_result else [],
                )

                bandit_findings, _ = _run_tool(
                    assessment.id, "bandit", repo_path, run_bandit, _bandit_findings
                )
                semgrep_findings, _ = _run_tool(
                    assessment.id, "semgrep", repo_path, run_semgrep, _semgrep_findings
                )
                gitleaks_findings, _ = _run_tool(
                    assessment.id, "gitleaks", repo_path, run_gitleaks, _gitleaks_findings
                )
                trivy_findings, _ = _run_tool(
                    assessment.id, "trivy", repo_path, run_trivy, _trivy_findings
                )
                all_findings += bandit_findings + semgrep_findings + gitleaks_findings
                all_findings += trivy_findings

                security_findings = [
                    finding for finding in all_findings if finding.category in _SECURITY_CATEGORIES
                ]
                security_score = compute_security_score(security_findings)

        except Exception as exc:  # noqa: BLE001 - only a catastrophic failure (e.g. clone) lands
            all_findings.append(_tool_error_finding(assessment.id, "assessment", exc))
            self._findings.bulk_create(all_findings)
            updated = self._assessments.update(assessment.id, status=AssessmentStatus.FAILED)
            assert updated is not None
            return updated

        self._findings.bulk_create(all_findings)
        updated = self._assessments.update(
            assessment.id,
            status=AssessmentStatus.COMPLETED,
            quality_score=quality_score,
            security_score=security_score,
        )
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
