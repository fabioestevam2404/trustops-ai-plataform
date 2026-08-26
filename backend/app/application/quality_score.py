from app.infrastructure.scanners.ruff_runner import RuffViolation

_MEDIUM_CODES = ("E", "F")


def _ruff_penalty(violations: list[RuffViolation]) -> float:
    penalty = 0.0
    for violation in violations:
        if violation.code.startswith(_MEDIUM_CODES):
            penalty += 2
        else:
            penalty += 0.5
    return min(penalty, 20.0)


def compute_quality_score(
    coverage_percent: float,
    pytest_passed: int,
    pytest_total: int,
    ruff_violations: list[RuffViolation],
) -> int:
    """Fórmula de partida do MVP: 60% cobertura + 40% taxa de sucesso dos testes,
    menos uma penalidade de Ruff (cap 20). Pesos não calibrados empiricamente —
    ver docs/trust-framework/README.md."""
    pass_rate = (pytest_passed / pytest_total * 100) if pytest_total > 0 else 0.0
    score = 0.6 * coverage_percent + 0.4 * pass_rate - _ruff_penalty(ruff_violations)
    return round(max(0.0, min(100.0, score)))
