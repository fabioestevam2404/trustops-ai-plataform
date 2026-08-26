from sqlalchemy.orm import Session

from app.domain.project import Project
from app.infrastructure.db.models import ProjectModel


def _to_entity(model: ProjectModel) -> Project:
    return Project(
        id=model.id,
        name=model.name,
        repository_url=model.repository_url,
        created_at=model.created_at,
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
        models = self._db.query(ProjectModel).order_by(ProjectModel.created_at.desc()).all()
        return [_to_entity(model) for model in models]

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
