from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_project_service
from app.api.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.application.project_service import ProjectService
from app.domain.project import ProjectNotFoundError

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate, service: ProjectService = Depends(get_project_service)
) -> ProjectRead:
    project = service.create(payload.name, payload.repository_url, payload.subdirectory)
    return ProjectRead.model_validate(project)


@router.get("", response_model=list[ProjectRead])
def list_projects(service: ProjectService = Depends(get_project_service)) -> list[ProjectRead]:
    return [ProjectRead.model_validate(project) for project in service.list()]


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: str, service: ProjectService = Depends(get_project_service)
) -> ProjectRead:
    try:
        project = service.get(project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ProjectRead.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    try:
        project = service.update(
            project_id, payload.name, payload.repository_url, payload.subdirectory
        )
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ProjectRead.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str, service: ProjectService = Depends(get_project_service)
) -> None:
    try:
        service.delete(project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
