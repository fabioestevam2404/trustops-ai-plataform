from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


SECURITY_CATEGORIES = {"security", "secrets", "misconfig"}


@dataclass
class Finding:
    id: str
    assessment_id: str
    tool: str
    severity: Severity
    category: str
    description: str


class FindingRepository(Protocol):
    def bulk_create(self, findings: list[Finding]) -> None: ...

    def list_for_assessment(self, assessment_id: str) -> list[Finding]: ...
