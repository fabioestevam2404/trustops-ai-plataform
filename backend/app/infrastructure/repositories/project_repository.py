from sqlalchemy.orm import Session

from app.domain.project import Project
from app.infrastructure.db.models import AssessmentModel, ProjectModel


def _to_entity(model: ProjectModel, latest_assessment: AssessmentModel | None = None) -> Project:
    return Project(
        id=model.id,
        name=model.name,
        repository_url=model.repository_url,
        created_at=model.created_at,
        latest_trust_score=latest_assessment.trust_score if latest_assessment else None,
        latest_certification_level=(
            latest_assessment.certification_level if latest_assessment else None
        ),
    )


class SqlAlchemyProjectRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, name: str, repository_url: str) -> Project:
        model = ProjectModel(name=name, repository_url=repository_url)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return _to_entity(model)

    def get(self, project_id: str) -> Project | None:
        model = self._db.get(ProjectModel, project_id)
        return _to_entity(model) if model else None

    def list(self) -> list[Project]:
        # One extra query total, not one per project — avoids an N+1 when the
        # dashboard wants each project's current score to sort/display alongside
        # the list. Newest-first order + dict.setdefault (keep only the first
        # assessment seen per project) picks the latest one per project without
        # relying on DISTINCT ON, which is Postgres-only and silently degrades to
        # a no-op on SQLite (used by the test suite) — this stays correct on both.
        latest_by_project: dict[str, AssessmentModel] = {}
        for assessment in (
            self._db.query(AssessmentModel)
            .order_by(AssessmentModel.created_at.desc(), AssessmentModel.id.desc())
            .all()
        ):
            latest_by_project.setdefault(assessment.project_id, assessment)

        models = self._db.query(ProjectModel).order_by(ProjectModel.created_at.desc()).all()
        return [_to_entity(model, latest_by_project.get(model.id)) for model in models]

    def update(
        self, project_id: str, name: str | None, repository_url: str | None
    ) -> Project | None:
        model = self._db.get(ProjectModel, project_id)
        if model is None:
            return None
        if name is not None:
            model.name = name
        if repository_url is not None:
            model.repository_url = repository_url
        self._db.commit()
        self._db.refresh(model)
        return _to_entity(model)

    def delete(self, project_id: str) -> bool:
        model = self._db.get(ProjectModel, project_id)
        if model is None:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
