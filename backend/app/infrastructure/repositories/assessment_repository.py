from sqlalchemy.orm import Session

from app.domain.assessment import Assessment, AssessmentStatus, CertificationLevel
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
        certification_level=(
            CertificationLevel(model.certification_level) if model.certification_level else None
        ),
        created_at=model.created_at,
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
            .order_by(AssessmentModel.created_at.asc())
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
        trust_score: int | None = None,
        certification_level: CertificationLevel | None = None,
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
        if trust_score is not None:
            model.trust_score = trust_score
        if certification_level is not None:
            model.certification_level = certification_level.value
        self._db.commit()
        self._db.refresh(model)
        return _to_entity(model)
