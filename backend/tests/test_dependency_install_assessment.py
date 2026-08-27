from pathlib import Path

from fastapi.testclient import TestClient


def _create_project(client: TestClient, repo_path: Path) -> dict:
    response = client.post(
        "/projects",
        json={"name": "deps-demo", "repository_url": str(repo_path)},
    )
    assert response.status_code == 201
    return response.json()


def test_quality_score_reflects_real_tests_when_deps_installed(
    client: TestClient, uv_repo_path: Path
) -> None:
    """Before dependency installation existed, a repo whose tests import a
    real third-party package would always show 0/0 tests (collection error)
    and quality_score=0. This proves the fix end to end."""
    project = _create_project(client, uv_repo_path)

    response = client.post(f"/projects/{project['id']}/assessments", json={})
    assert response.status_code == 201
    assessment = response.json()
    assert assessment["status"] == "COMPLETED"
    assert assessment["quality_score"] is not None
    assert assessment["quality_score"] > 0

    findings = client.get(f"/assessments/{assessment['id']}/findings").json()
    pytest_summary = next(
        f for f in findings if f["tool"] == "pytest" and "passed" in f["description"]
    )
    assert pytest_summary["description"] == "2/2 tests passed"

    install_finding = next(f for f in findings if f["tool"] == "dependency-install")
    assert "installed via uv" in install_finding["description"]

    install_report = client.get(f"/assessments/{assessment['id']}/reports/dependency-install")
    assert install_report.status_code == 200
    assert "uv sync" in install_report.text
