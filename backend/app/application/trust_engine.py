from app.domain.assessment import CertificationLevel
from app.domain.finding import SECURITY_CATEGORIES, Finding, Severity

TRUST_WEIGHTS = {"quality": 0.5, "security": 0.5}
TRUST_WEIGHTS_WITH_AI = {"quality": 0.4, "security": 0.4, "ai_trust": 0.2}

_BLOCKING_CATEGORIES = SECURITY_CATEGORIES | {"ai-trust"}


def compute_trust_score(
    quality_score: int, security_score: int, ai_trust_score: int | None = None
) -> int:
    """Fórmula de partida do MVP: média ponderada dos sub-scores aplicáveis.
    Sem avaliação de IA (repositório sem dataset em ai-eval/), usa TRUST_WEIGHTS
    (50/50 quality/security, comportamento original das Sprints 4-6). Com IA
    aplicável, usa TRUST_WEIGHTS_WITH_AI. Pesos não calibrados empiricamente —
    ver docs/trust-framework/README.md."""
    if ai_trust_score is None:
        score = (
            TRUST_WEIGHTS["quality"] * quality_score + TRUST_WEIGHTS["security"] * security_score
        )
    else:
        score = (
            TRUST_WEIGHTS_WITH_AI["quality"] * quality_score
            + TRUST_WEIGHTS_WITH_AI["security"] * security_score
            + TRUST_WEIGHTS_WITH_AI["ai_trust"] * ai_trust_score
        )
    return round(score)


def classify_certification(trust_score: int, findings: list[Finding]) -> CertificationLevel:
    """Qualquer finding CRITICAL de categoria de segurança OU de IA (ai-trust —
    ex. prompt injection bem-sucedido) bloqueia a certificação, independente do
    trust_score — mesma regra da seção 6 da especificação
    (`IF vulnerabilities.critical > 0: Certification = BLOCKED`)."""
    has_critical_blocking_finding = any(
        finding.severity == Severity.CRITICAL and finding.category in _BLOCKING_CATEGORIES
        for finding in findings
    )
    if has_critical_blocking_finding:
        return CertificationLevel.BLOCKED

    if trust_score >= 95:
        return CertificationLevel.ENTERPRISE_TRUST
    if trust_score >= 85:
        return CertificationLevel.HIGH_TRUST
    if trust_score >= 75:
        return CertificationLevel.TRUSTED
    return CertificationLevel.FOUNDATION
