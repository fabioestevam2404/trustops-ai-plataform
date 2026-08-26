from pydantic import BaseModel, ConfigDict

from app.domain.assessment import CertificationLevel


class AssessmentReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project: str
    version: str
    trust_score: int | None
    certification_level: CertificationLevel | None
    status: str
    findings_by_severity: dict[str, int]
