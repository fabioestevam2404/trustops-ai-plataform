from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies import (
    get_assessment_service,
    get_certificate_service,
    get_project_service,
)
from app.api.schemas.assessment import AssessmentCreate, AssessmentRead, FindingRead
from app.api.schemas.certificate import CertificateRead
from app.api.schemas.report import AssessmentReportRead
from app.application.assessment_service import AssessmentService
from app.application.certificate_service import CertificateService
from app.application.project_service import ProjectService
from app.application.report import build_assessment_report
from app.application.risk_register import build_risk_register
from app.domain.assessment import AssessmentNotFoundError, AssessmentStatus
from app.domain.project import ProjectNotFoundError
from app.infrastructure import evidence_store

router = APIRouter(tags=["assessments"])


@router.post(
    "/projects/{project_id}/assessments",
    response_model=AssessmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_assessment(
    project_id: str,
    payload: AssessmentCreate,
    service: AssessmentService = Depends(get_assessment_service),
) -> AssessmentRead:
    try:
        assessment = service.run(project_id, payload.version)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return AssessmentRead.model_validate(assessment)


@router.get("/projects/{project_id}/assessments", response_model=list[AssessmentRead])
def list_assessments(
    project_id: str, service: AssessmentService = Depends(get_assessment_service)
) -> list[AssessmentRead]:
    return [
        AssessmentRead.model_validate(assessment)
        for assessment in service.list_for_project(project_id)
    ]


@router.get("/assessments/{assessment_id}", response_model=AssessmentRead)
def get_assessment(
    assessment_id: str, service: AssessmentService = Depends(get_assessment_service)
) -> AssessmentRead:
    try:
        assessment = service.get(assessment_id)
    except AssessmentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return AssessmentRead.model_validate(assessment)


@router.get("/assessments/{assessment_id}/findings", response_model=list[FindingRead])
def list_findings(
    assessment_id: str, service: AssessmentService = Depends(get_assessment_service)
) -> list[FindingRead]:
    findings = service.list_findings(assessment_id)
    return [FindingRead.model_validate(finding) for finding in findings]


@router.get("/assessments/{assessment_id}/reports/{tool}")
def get_raw_evidence_report(assessment_id: str, tool: str) -> Response:
    content = evidence_store.read(assessment_id, tool)
    if content is None:
        raise HTTPException(status_code=404, detail=f"report for tool '{tool}' not found")
    return Response(content=content, media_type="application/json")


@router.get("/assessments/{assessment_id}/report", response_model=AssessmentReportRead)
def get_assessment_report(
    assessment_id: str,
    assessment_service: AssessmentService = Depends(get_assessment_service),
    project_service: ProjectService = Depends(get_project_service),
) -> AssessmentReportRead:
    try:
        assessment = assessment_service.get(assessment_id)
    except AssessmentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    project = project_service.get(assessment.project_id)
    findings = assessment_service.list_findings(assessment_id)
    report = build_assessment_report(project, assessment, findings)
    return AssessmentReportRead.model_validate(report)


@router.get("/assessments/{assessment_id}/certificate", response_model=CertificateRead)
def get_certificate(
    assessment_id: str,
    assessment_service: AssessmentService = Depends(get_assessment_service),
    certificate_service: CertificateService = Depends(get_certificate_service),
) -> CertificateRead:
    try:
        assessment_service.get(assessment_id)  # confirms the assessment exists
    except AssessmentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    certificate = certificate_service.get_by_assessment(assessment_id)
    if certificate is None:
        raise HTTPException(status_code=404, detail="no certificate issued for this assessment")
    return CertificateRead.model_validate(certificate)


@router.get("/projects/{project_id}/certificates", response_model=list[CertificateRead])
def list_certificates(
    project_id: str, certificate_service: CertificateService = Depends(get_certificate_service)
) -> list[CertificateRead]:
    certificates = certificate_service.list_for_project(project_id)
    return [CertificateRead.model_validate(certificate) for certificate in certificates]


@router.get("/projects/{project_id}/risk-register", response_model=list[FindingRead])
def get_risk_register(
    project_id: str, assessment_service: AssessmentService = Depends(get_assessment_service)
) -> list[FindingRead]:
    assessments = assessment_service.list_for_project(project_id)
    completed = [a for a in assessments if a.status == AssessmentStatus.COMPLETED]
    if not completed:
        return []
    latest = max(completed, key=lambda a: a.created_at)
    findings = assessment_service.list_findings(latest.id)
    return [FindingRead.model_validate(finding) for finding in build_risk_register(findings)]
