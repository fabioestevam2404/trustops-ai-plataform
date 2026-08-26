from sqlalchemy.orm import Session

from app.domain.assessment import CertificationLevel
from app.domain.certificate import Certificate, CertificateStatus
from app.infrastructure.db.models import CertificateModel


def _to_entity(model: CertificateModel) -> Certificate:
    return Certificate(
        id=model.id,
        assessment_id=model.assessment_id,
        project_id=model.project_id,
        version=model.version,
        certification_level=CertificationLevel(model.certification_level),
        status=CertificateStatus(model.status),
        issued_at=model.issued_at,
    )


class SqlAlchemyCertificateRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        assessment_id: str,
        project_id: str,
        version: str,
        certification_level: CertificationLevel,
    ) -> Certificate:
        model = CertificateModel(
            assessment_id=assessment_id,
            project_id=project_id,
            version=version,
            certification_level=certification_level.value,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return _to_entity(model)

    def get_by_assessment(self, assessment_id: str) -> Certificate | None:
        model = (
            self._db.query(CertificateModel)
            .filter(CertificateModel.assessment_id == assessment_id)
            .first()
        )
        return _to_entity(model) if model else None

    def list_for_project(self, project_id: str) -> list[Certificate]:
        models = (
            self._db.query(CertificateModel)
            .filter(CertificateModel.project_id == project_id)
            .order_by(CertificateModel.issued_at.asc())
            .all()
        )
        return [_to_entity(model) for model in models]
