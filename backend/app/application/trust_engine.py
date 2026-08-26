from app.domain.assessment import CertificationLevel
from app.domain.finding import SECURITY_CATEGORIES, Finding, Severity

TRUST_WEIGHTS = {"quality": 0.5, "security": 0.5}


def compute_trust_score(quality_score: int, security_score: int) -> int:
    """Fórmula de partida do MVP: média ponderada de quality_score e security_score,
    pesos iguais (TRUST_WEIGHTS). Não calibrado empiricamente — ver
    docs/trust-framework/README.md."""
    score = (
        TRUST_WEIGHTS["quality"] * quality_score + TRUST_WEIGHTS["security"] * security_score
    )
    return round(score)


def classify_certification(trust_score: int, findings: list[Finding]) -> CertificationLevel:
    """Qualquer finding CRITICAL de categoria de segurança bloqueia a certificação,
    independente do trust_score — mesma regra da seção 6 da especificação
    (`IF vulnerabilities.critical > 0: Certification = BLOCKED`)."""
    has_critical_security_finding = any(
        finding.severity == Severity.CRITICAL and finding.category in SECURITY_CATEGORIES
        for finding in findings
    )
    if has_critical_security_finding:
        return CertificationLevel.BLOCKED

    if trust_score >= 95:
        return CertificationLevel.ENTERPRISE_TRUST
    if trust_score >= 85:
        return CertificationLevel.HIGH_TRUST
    if trust_score >= 75:
        return CertificationLevel.TRUSTED
    return CertificationLevel.FOUNDATION
