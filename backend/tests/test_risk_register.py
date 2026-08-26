from app.application.risk_register import build_risk_register
from app.domain.finding import Finding, Severity


def _finding(severity: Severity, id_: str) -> Finding:
    return Finding(
        id=id_, assessment_id="a1", tool="test", severity=severity, category="security",
        description="x",
    )


def test_build_risk_register_keeps_only_critical_and_high() -> None:
    findings = [
        _finding(Severity.CRITICAL, "1"),
        _finding(Severity.HIGH, "2"),
        _finding(Severity.MEDIUM, "3"),
        _finding(Severity.LOW, "4"),
        _finding(Severity.INFO, "5"),
    ]
    register = build_risk_register(findings)
    assert {finding.id for finding in register} == {"1", "2"}


def test_build_risk_register_empty_when_no_risks() -> None:
    findings = [_finding(Severity.LOW, "1"), _finding(Severity.INFO, "2")]
    assert build_risk_register(findings) == []
