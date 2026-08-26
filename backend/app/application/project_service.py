from app.domain.project import Project, ProjectNotFoundError, ProjectRepository


class ProjectService:
    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    def create(self, name: str, repository_url: str) -> Project:
        return self._repository.create(name, repository_url)

    def get(self, project_id: str) -> Project:
        project = self._repository.get(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)
        return project

    def list(self) -> list[Project]:
        return self._repository.list()

    def update(self, project_id: str, name: str | None, repository_url: str | None) -> Project:
        project = self._repository.update(project_id, name, repository_url)
        if project is None:
            raise ProjectNotFoundError(project_id)
        return project

    def delete(self, project_id: str) -> None:
        deleted = self._repository.delete(project_id)
        if not deleted:
            raise ProjectNotFoundError(project_id)
