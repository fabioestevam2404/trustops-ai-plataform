from app.application.scoring import score_from_penalties
from app.domain.finding import Finding


def compute_ai_trust_score(findings: list[Finding]) -> int:
    return score_from_penalties(findings)
