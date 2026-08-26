from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies import get_assessment_service
from app.api.schemas.assessment import AssessmentCreate, AssessmentRead, FindingRead
from app.application.assessment_service import AssessmentService
from app.domain.assessment import AssessmentNotFoundError
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
def get_report(assessment_id: str, tool: str) -> Response:
    content = evidence_store.read(assessment_id, tool)
    if content is None:
        raise HTTPException(status_code=404, detail=f"report for tool '{tool}' not found")
    return Response(content=content, media_type="application/json")
