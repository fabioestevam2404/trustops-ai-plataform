from pathlib import Path

from fastapi.testclient import TestClient


def _create_project(client: TestClient, demo_repo_path: Path) -> dict:
    response = client.post(
        "/projects",
        json={"name": "demo", "repository_url": str(demo_repo_path)},
    )
    assert response.status_code == 201
    return response.json()


def test_create_assessment_completes_and_reports_findings(
    client: TestClient, demo_repo_path: Path
) -> None:
    project = _create_project(client, demo_repo_path)

    response = client.post(f"/projects/{project['id']}/assessments", json={})
    assert response.status_code == 201
    assessment = response.json()
    assert assessment["status"] == "COMPLETED"
    assert assessment["quality_score"] is not None
    assert 0 <= assessment["quality_score"] <= 100

    findings = client.get(f"/assessments/{assessment['id']}/findings").json()
    tools = {finding["tool"] for finding in findings}
    assert tools == {"pytest", "coverage", "ruff"}

    ruff_findings = [f for f in findings if f["tool"] == "ruff"]
    assert any("F401" in f["description"] for f in ruff_findings)

    assert client.get(f"/assessments/{assessment['id']}/reports/pytest").status_code == 200
    assert client.get(f"/assessments/{assessment['id']}/reports/coverage").status_code == 200
    assert client.get(f"/assessments/{assessment['id']}/reports/ruff").status_code == 200


def test_create_assessment_project_not_found(client: TestClient) -> None:
    response = client.post("/projects/does-not-exist/assessments", json={})
    assert response.status_code == 404


def test_list_assessments_for_project(client: TestClient, demo_repo_path: Path) -> None:
    project = _create_project(client, demo_repo_path)
    client.post(f"/projects/{project['id']}/assessments", json={})

    response = client.get(f"/projects/{project['id']}/assessments")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_assessment_not_found(client: TestClient) -> None:
    response = client.get("/assessments/does-not-exist")
    assert response.status_code == 404


def test_get_report_unknown_tool(client: TestClient, demo_repo_path: Path) -> None:
    project = _create_project(client, demo_repo_path)
    assessment = client.post(f"/projects/{project['id']}/assessments", json={}).json()

    response = client.get(f"/assessments/{assessment['id']}/reports/unknown-tool")
    assert response.status_code == 404
