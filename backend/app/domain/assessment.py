from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class AssessmentStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class CertificationLevel(str, Enum):
    BLOCKED = "BLOCKED"
    FOUNDATION = "FOUNDATION"
    TRUSTED = "TRUSTED"
    HIGH_TRUST = "HIGH_TRUST"
    ENTERPRISE_TRUST = "ENTERPRISE_TRUST"


@dataclass
class Assessment:
    id: str
    project_id: str
    version: str
    status: AssessmentStatus
    quality_score: int | None
    security_score: int | None
    trust_score: int | None
    certification_level: CertificationLevel | None


class AssessmentNotFoundError(Exception):
    def __init__(self, assessment_id: str) -> None:
        self.assessment_id = assessment_id
        super().__init__(f"Assessment {assessment_id} not found")


class AssessmentRepository(Protocol):
    def create(self, project_id: str, version: str) -> Assessment: ...

    def get(self, assessment_id: str) -> Assessment | None: ...

    def list_for_project(self, project_id: str) -> list[Assessment]: ...

    def update(
        self,
        assessment_id: str,
        *,
        version: str | None = None,
        status: AssessmentStatus | None = None,
        quality_score: int | None = None,
        security_score: int | None = None,
        trust_score: int | None = None,
        certification_level: CertificationLevel | None = None,
    ) -> Assessment | None: ...
