from app.domain.finding import Finding, Severity

SEVERITY_PENALTIES = {
    Severity.CRITICAL: 25.0,
    Severity.HIGH: 10.0,
    Severity.MEDIUM: 3.0,
    Severity.LOW: 0.5,
    Severity.INFO: 0.0,
}


def score_from_penalties(findings: list[Finding]) -> int:
    """100 menos uma penalidade por severidade (ver SEVERITY_PENALTIES), cap [0, 100].
    Fórmula compartilhada por security_score e ai_trust_score — pesos não calibrados
    empiricamente, ver docs/trust-framework/README.md."""
    penalty = sum(SEVERITY_PENALTIES[finding.severity] for finding in findings)
    return round(max(0.0, min(100.0, 100.0 - penalty)))
