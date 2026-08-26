from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.assessment_service import AssessmentService
from app.application.project_service import ProjectService
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.assessment_repository import SqlAlchemyAssessmentRepository
from app.infrastructure.repositories.finding_repository import SqlAlchemyFindingRepository
from app.infrastructure.repositories.project_repository import SqlAlchemyProjectRepository


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(SqlAlchemyProjectRepository(db))


def get_assessment_service(db: Session = Depends(get_db)) -> AssessmentService:
    return AssessmentService(
        assessment_repository=SqlAlchemyAssessmentRepository(db),
        finding_repository=SqlAlchemyFindingRepository(db),
        project_repository=SqlAlchemyProjectRepository(db),
    )
