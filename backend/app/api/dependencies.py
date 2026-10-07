from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.api_key_service import ApiKeyService
from app.application.assessment_service import AssessmentService
from app.application.certificate_service import CertificateService
from app.application.project_service import ProjectService
from app.application.user_service import UserService
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.api_key_repository import SqlAlchemyApiKeyRepository
from app.infrastructure.repositories.assessment_repository import SqlAlchemyAssessmentRepository
from app.infrastructure.repositories.certificate_repository import (
    SqlAlchemyCertificateRepository,
)
from app.infrastructure.repositories.finding_repository import SqlAlchemyFindingRepository
from app.infrastructure.repositories.project_repository import SqlAlchemyProjectRepository
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository


def get_api_key_service(db: Session = Depends(get_db)) -> ApiKeyService:
    return ApiKeyService(SqlAlchemyApiKeyRepository(db))


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(SqlAlchemyUserRepository(db))


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(SqlAlchemyProjectRepository(db))


def get_certificate_service(db: Session = Depends(get_db)) -> CertificateService:
    return CertificateService(SqlAlchemyCertificateRepository(db))


def get_assessment_service(db: Session = Depends(get_db)) -> AssessmentService:
    return AssessmentService(
        assessment_repository=SqlAlchemyAssessmentRepository(db),
        finding_repository=SqlAlchemyFindingRepository(db),
        project_repository=SqlAlchemyProjectRepository(db),
        certificate_service=get_certificate_service(db),
    )
