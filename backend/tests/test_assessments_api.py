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
    assert assessment["security_score"] is not None
    assert 0 <= assessment["security_score"] <= 100

    findings = client.get(f"/assessments/{assessment['id']}/findings").json()
    tools = {finding["tool"] for finding in findings}
    expected_tools = {"pytest", "coverage", "ruff", "bandit", "semgrep", "gitleaks", "trivy"}
    assert expected_tools <= tools
    assert "execution" not in {f["category"] for f in findings}, findings

    ruff_findings = [f for f in findings if f["tool"] == "ruff"]
    assert any("F401" in f["description"] for f in ruff_findings)

    # the synthetic AWS key in insecure.py should be caught by both secret scanners
    assert any(f["tool"] == "gitleaks" and f["severity"] == "CRITICAL" for f in findings)
    assert any(f["tool"] == "trivy" and f["category"] == "secrets" for f in findings)
    # eval()/shell=True should be caught by both Bandit and our Semgrep ruleset
    assert any(f["tool"] == "bandit" for f in findings)
    assert any(f["tool"] == "semgrep" for f in findings)

    for tool in ("pytest", "coverage", "ruff", "bandit", "semgrep", "gitleaks", "trivy"):
        report = client.get(f"/assessments/{assessment['id']}/reports/{tool}")
        assert report.status_code == 200, tool


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
