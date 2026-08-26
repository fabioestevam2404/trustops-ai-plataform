from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol

from app.domain.assessment import CertificationLevel


class CertificateStatus(str, Enum):
    ISSUED = "ISSUED"


@dataclass
class Certificate:
    id: str
    assessment_id: str
    project_id: str
    version: str
    certification_level: CertificationLevel
    status: CertificateStatus
    issued_at: datetime


class CertificateRepository(Protocol):
    def create(
        self,
        assessment_id: str,
        project_id: str,
        version: str,
        certification_level: CertificationLevel,
    ) -> Certificate: ...

    def get_by_assessment(self, assessment_id: str) -> Certificate | None: ...

    def list_for_project(self, project_id: str) -> list[Certificate]: ...
