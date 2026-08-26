from app.application.trust_engine import classify_certification, compute_trust_score
from app.domain.assessment import CertificationLevel
from app.domain.finding import Finding, Severity


def _finding(severity: Severity, category: str) -> Finding:
    return Finding(
        id="f1",
        assessment_id="a1",
        tool="test",
        severity=severity,
        category=category,
        description="synthetic",
    )


def test_compute_trust_score_averages_equally_weighted() -> None:
    assert compute_trust_score(quality_score=100, security_score=100) == 100
    assert compute_trust_score(quality_score=0, security_score=0) == 0
    assert compute_trust_score(quality_score=80, security_score=60) == 70


def test_compute_trust_score_without_ai_ignores_ai_weight() -> None:
    # No ai_trust_score passed -> same 50/50 formula as before Sprint 7 (no regression).
    assert compute_trust_score(quality_score=80, security_score=60, ai_trust_score=None) == 70


def test_compute_trust_score_with_ai_uses_three_way_weights() -> None:
    assert compute_trust_score(quality_score=100, security_score=100, ai_trust_score=100) == 100
    assert compute_trust_score(quality_score=100, security_score=100, ai_trust_score=0) == 80


def test_classify_certification_thresholds() -> None:
    assert classify_certification(95, []) == CertificationLevel.ENTERPRISE_TRUST
    assert classify_certification(94, []) == CertificationLevel.HIGH_TRUST
    assert classify_certification(85, []) == CertificationLevel.HIGH_TRUST
    assert classify_certification(84, []) == CertificationLevel.TRUSTED
    assert classify_certification(75, []) == CertificationLevel.TRUSTED
    assert classify_certification(74, []) == CertificationLevel.FOUNDATION
    assert classify_certification(0, []) == CertificationLevel.FOUNDATION


def test_classify_certification_blocked_by_critical_security_finding() -> None:
    findings = [_finding(Severity.CRITICAL, "secrets")]
    assert classify_certification(100, findings) == CertificationLevel.BLOCKED


def test_classify_certification_not_blocked_by_critical_execution_finding() -> None:
    # A scanner crash (category=execution) is not a real vulnerability — must not block.
    findings = [_finding(Severity.CRITICAL, "execution")]
    assert classify_certification(100, findings) == CertificationLevel.ENTERPRISE_TRUST


def test_classify_certification_not_blocked_by_non_critical_security_finding() -> None:
    findings = [_finding(Severity.HIGH, "security")]
    assert classify_certification(100, findings) == CertificationLevel.ENTERPRISE_TRUST


def test_classify_certification_blocked_by_critical_ai_trust_finding() -> None:
    # A successful prompt injection is as serious as a critical vulnerability.
    findings = [_finding(Severity.CRITICAL, "ai-trust")]
    assert classify_certification(100, findings) == CertificationLevel.BLOCKED


def test_classify_certification_not_blocked_by_high_ai_trust_finding() -> None:
    # A hallucination (HIGH, not CRITICAL) is flagged but doesn't block.
    findings = [_finding(Severity.HIGH, "ai-trust")]
    assert classify_certification(100, findings) == CertificationLevel.ENTERPRISE_TRUST
