from app.domain.finding import Finding, Severity

_PENALTY_BY_SEVERITY = {
    Severity.CRITICAL: 25.0,
    Severity.HIGH: 10.0,
    Severity.MEDIUM: 3.0,
    Severity.LOW: 0.5,
    Severity.INFO: 0.0,
}


def compute_security_score(findings: list[Finding]) -> int:
    """Fórmula de partida do MVP: 100 menos uma penalidade por severidade
    (CRITICAL -25, HIGH -10, MEDIUM -3, LOW -0.5). Pesos não calibrados
    empiricamente — ver docs/trust-framework/README.md."""
    penalty = sum(_PENALTY_BY_SEVERITY[finding.severity] for finding in findings)
    return round(max(0.0, min(100.0, 100.0 - penalty)))
