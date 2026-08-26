from sqlalchemy.orm import Session

from app.domain.assessment import Assessment, AssessmentStatus
from app.infrastructure.db.models import AssessmentModel


def _to_entity(model: AssessmentModel) -> Assessment:
    return Assessment(
        id=model.id,
        project_id=model.project_id,
        version=model.version,
        status=AssessmentStatus(model.status),
        quality_score=model.quality_score,
        security_score=model.security_score,
        trust_score=model.trust_score,
    )


class SqlAlchemyAssessmentRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, project_id: str, version: str) -> Assessment:
        model = AssessmentModel(
            project_id=project_id, version=version, status=AssessmentStatus.PENDING.value
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return _to_entity(model)

    def get(self, assessment_id: str) -> Assessment | None:
        model = self._db.get(AssessmentModel, assessment_id)
        return _to_entity(model) if model else None

    def list_for_project(self, project_id: str) -> list[Assessment]:
        models = (
            self._db.query(AssessmentModel)
            .filter(AssessmentModel.project_id == project_id)
            .all()
        )
        return [_to_entity(model) for model in models]

    def update(
        self,
        assessment_id: str,
        *,
        version: str | None = None,
        status: AssessmentStatus | None = None,
        quality_score: int | None = None,
        security_score: int | None = None,
    ) -> Assessment | None:
        model = self._db.get(AssessmentModel, assessment_id)
        if model is None:
            return None
        if version is not None:
            model.version = version
        if status is not None:
            model.status = status.value
        if quality_score is not None:
            model.quality_score = quality_score
        if security_score is not None:
            model.security_score = security_score
        self._db.commit()
        self._db.refresh(model)
        return _to_entity(model)
