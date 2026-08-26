from sqlalchemy.orm import Session

from app.domain.finding import Finding, Severity
from app.infrastructure.db.models import FindingModel


def _to_entity(model: FindingModel) -> Finding:
    return Finding(
        id=model.id,
        assessment_id=model.assessment_id,
        tool=model.tool,
        severity=Severity(model.severity),
        category=model.category,
        description=model.description,
    )


class SqlAlchemyFindingRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def bulk_create(self, findings: list[Finding]) -> None:
        models = [
            FindingModel(
                assessment_id=finding.assessment_id,
                tool=finding.tool,
                severity=finding.severity.value,
                category=finding.category,
                description=finding.description,
            )
            for finding in findings
        ]
        self._db.add_all(models)
        self._db.commit()

    def list_for_assessment(self, assessment_id: str) -> list[Finding]:
        models = (
            self._db.query(FindingModel)
            .filter(FindingModel.assessment_id == assessment_id)
            .all()
        )
        return [_to_entity(model) for model in models]
