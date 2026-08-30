from pathlib import Path

from fastapi.testclient import TestClient


def _create_project(client: TestClient, repo_path: Path, subdirectory: str | None) -> dict:
    response = client.post(
        "/projects",
        json={
            "name": "monorepo-demo",
            "repository_url": str(repo_path),
            "subdirectory": subdirectory,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_project_create_persists_subdirectory(client: TestClient) -> None:
    project = _create_project(client, Path("/tmp/whatever"), "backend")
    assert project["subdirectory"] == "backend"

    fetched = client.get(f"/projects/{project['id']}").json()
    assert fetched["subdirectory"] == "backend"


def test_project_create_without_subdirectory_defaults_to_none(client: TestClient) -> None:
    project = _create_project(client, Path("/tmp/whatever"), None)
    assert project["subdirectory"] is None


def test_quality_scanners_scope_to_subdirectory_security_scans_whole_repo(
    client: TestClient, monorepo_path: Path
) -> None:
    project = _create_project(client, monorepo_path, "backend")

    response = client.post(f"/projects/{project['id']}/assessments", json={})
    assert response.status_code == 201
    assessment = response.json()
    assert assessment["status"] == "COMPLETED"

    # Quality: dependency install found backend/requirements.txt (not "not
    # applicable", which is what it'd say if it looked at the repo root
    # instead) and the tests inside backend/ actually ran and passed.
    assert assessment["quality_score"] is not None
    assert assessment["quality_score"] > 0

    findings = client.get(f"/assessments/{assessment['id']}/findings").json()

    install_finding = next(f for f in findings if f["tool"] == "dependency-install")
    assert "installed via" in install_finding["description"]

    pytest_summary = next(
        f for f in findings if f["tool"] == "pytest" and "passed" in f["description"]
    )
    assert pytest_summary["description"] == "2/2 tests passed"

    # Quality scoping: no ruff finding should reference the root-level file —
    # ruff never should have looked outside backend/.
    ruff_findings = [f for f in findings if f["tool"] == "ruff"]
    assert not any("root_secret.py" in f["description"] for f in ruff_findings)

    # Security: gitleaks must still have caught the root-level secret even
    # though it lives outside the quality-scanned subdirectory.
    gitleaks_findings = [f for f in findings if f["tool"] == "gitleaks"]
    assert any("root_secret.py" in f["description"] for f in gitleaks_findings)
    assert any(f["severity"] == "CRITICAL" for f in gitleaks_findings)
