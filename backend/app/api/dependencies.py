from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.project_service import ProjectService
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.project_repository import SqlAlchemyProjectRepository


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(SqlAlchemyProjectRepository(db))
