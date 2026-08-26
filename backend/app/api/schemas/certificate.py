from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.assessment import CertificationLevel
from app.domain.certificate import CertificateStatus


class CertificateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    assessment_id: str
    project_id: str
    version: str
    certification_level: CertificationLevel
    status: CertificateStatus
    issued_at: datetime
