from dataclasses import dataclass

from app.domain.assessment import Assessment, CertificationLevel
from app.domain.finding import Finding, Severity
from app.domain.project import Project


@dataclass
class AssessmentReport:
    project: str
    version: str
    trust_score: int | None
    certification_level: CertificationLevel | None
    status: str
    findings_by_severity: dict[str, int]


def build_assessment_report(
    project: Project, assessment: Assessment, findings: list[Finding]
) -> AssessmentReport:
    if assessment.certification_level is None:
        status = "PENDING"
    elif assessment.certification_level == CertificationLevel.BLOCKED:
        status = "BLOCKED"
    else:
        status = "APPROVED"

    findings_by_severity = {severity.value.lower(): 0 for severity in Severity}
    for finding in findings:
        findings_by_severity[finding.severity.value.lower()] += 1

    return AssessmentReport(
        project=project.name,
        version=assessment.version,
        trust_score=assessment.trust_score,
        certification_level=assessment.certification_level,
        status=status,
        findings_by_severity=findings_by_severity,
    )
