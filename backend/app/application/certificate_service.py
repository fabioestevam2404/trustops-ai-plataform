from app.domain.assessment import CertificationLevel
from app.domain.certificate import Certificate, CertificateRepository


class CertificateService:
    def __init__(self, repository: CertificateRepository) -> None:
        self._repository = repository

    def issue(
        self,
        assessment_id: str,
        project_id: str,
        version: str,
        certification_level: CertificationLevel,
    ) -> Certificate:
        return self._repository.create(assessment_id, project_id, version, certification_level)

    def get_by_assessment(self, assessment_id: str) -> Certificate | None:
        return self._repository.get_by_assessment(assessment_id)

    def list_for_project(self, project_id: str) -> list[Certificate]:
        return self._repository.list_for_project(project_id)
