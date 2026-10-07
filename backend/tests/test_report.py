from datetime import UTC, datetime

from app.application.report import build_assessment_report
from app.domain.assessment import Assessment, AssessmentStatus, CertificationLevel
from app.domain.finding import Finding, Severity
from app.domain.project import Project

_NOW = datetime.now(UTC)


def _project() -> Project:
    return Project(id="p1", name="example-api", repository_url="https://x", created_at=_NOW)


def _assessment(
    certification_level: CertificationLevel | None, trust_score: int | None
) -> Assessment:
    return Assessment(
        id="a1",
        project_id="p1",
        version="main@abc123",
        status=AssessmentStatus.COMPLETED,
        quality_score=90,
        security_score=80,
        ai_trust_score=None,
        trust_score=trust_score,
        certification_level=certification_level,
        created_at=_NOW,
    )


def _finding(severity: Severity) -> Finding:
    return Finding(
        id="f1", assessment_id="a1", tool="test", severity=severity, category="security",
        description="x",
    )


def test_build_report_approved() -> None:
    report = build_assessment_report(
        _project(), _assessment(CertificationLevel.HIGH_TRUST, 87), []
    )
    assert report.project == "example-api"
    assert report.version == "main@abc123"
    assert report.trust_score == 87
    assert report.certification_level == CertificationLevel.HIGH_TRUST
    assert report.status == "APPROVED"


def test_build_report_blocked() -> None:
    report = build_assessment_report(_project(), _assessment(CertificationLevel.BLOCKED, 25), [])
    assert report.status == "BLOCKED"


def test_build_report_pending_when_no_certification_yet() -> None:
    report = build_assessment_report(_project(), _assessment(None, None), [])
    assert report.status == "PENDING"


def test_build_report_counts_findings_by_severity() -> None:
    findings = [
        _finding(Severity.CRITICAL),
        _finding(Severity.CRITICAL),
        _finding(Severity.HIGH),
        _finding(Severity.INFO),
    ]
    report = build_assessment_report(
        _project(), _assessment(CertificationLevel.FOUNDATION, 40), findings
    )
    assert report.findings_by_severity == {
        "critical": 2,
        "high": 1,
        "medium": 0,
        "low": 0,
        "info": 1,
    }
