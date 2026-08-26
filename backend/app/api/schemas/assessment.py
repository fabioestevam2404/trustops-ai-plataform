from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.assessment import AssessmentStatus, CertificationLevel
from app.domain.finding import Severity


class AssessmentCreate(BaseModel):
    version: str | None = None


class AssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    version: str
    status: AssessmentStatus
    quality_score: int | None
    security_score: int | None
    ai_trust_score: int | None
    trust_score: int | None
    certification_level: CertificationLevel | None
    created_at: datetime


class FindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    assessment_id: str
    tool: str
    severity: Severity
    category: str
    description: str
