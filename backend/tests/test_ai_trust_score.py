from app.application.ai_trust_score import compute_ai_trust_score
from app.domain.finding import Finding, Severity
from app.infrastructure.scanners.ai_trust_runner import _lexical_overlap


def _finding(severity: Severity) -> Finding:
    return Finding(
        id="f1", assessment_id="a1", tool="ai-trust", severity=severity, category="ai-trust",
        description="x",
    )


def test_compute_ai_trust_score_no_findings_is_perfect() -> None:
    assert compute_ai_trust_score([]) == 100


def test_compute_ai_trust_score_critical_penalty() -> None:
    assert compute_ai_trust_score([_finding(Severity.CRITICAL)]) == 75


def test_compute_ai_trust_score_clamped_at_zero() -> None:
    findings = [_finding(Severity.CRITICAL) for _ in range(10)]
    assert compute_ai_trust_score(findings) == 0


def test_lexical_overlap_identical_text_is_one() -> None:
    assert _lexical_overlap("Paris is the capital", "Paris is the capital") == 1.0


def test_lexical_overlap_unrelated_text_is_low() -> None:
    assert _lexical_overlap("the moon landing", "capital of France is Paris") == 0.0


def test_lexical_overlap_empty_string_is_zero() -> None:
    assert _lexical_overlap("", "some context") == 0.0
