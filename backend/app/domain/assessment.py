from dataclasses import dataclass
from enum import Enum


class AssessmentStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Assessment:
    id: str
    project_id: str
    version: str
    status: AssessmentStatus
    trust_score: int | None
