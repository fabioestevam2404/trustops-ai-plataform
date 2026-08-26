from app.domain.finding import Finding, Severity

_RISK_SEVERITIES = {Severity.CRITICAL, Severity.HIGH}


def build_risk_register(findings: list[Finding]) -> list[Finding]:
    """Riscos abertos = findings CRITICAL/HIGH do assessment mais recente concluído."""
    return [finding for finding in findings if finding.severity in _RISK_SEVERITIES]
