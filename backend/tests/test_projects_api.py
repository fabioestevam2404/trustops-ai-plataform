from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.infrastructure.db.models import AssessmentModel


def _create_project(
    client: TestClient, name: str = "example-api", repository_url: str = ""
) -> dict:
    response = client.post(
        "/projects",
        json={
            "name": name,
            "repository_url": repository_url or "https://github.com/org/example-api",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_project(client: TestClient) -> None:
    project = _create_project(client)
    assert project["name"] == "example-api"
    assert project["repository_url"] == "https://github.com/org/example-api"
    assert "id" in project
    assert "created_at" in project


def test_list_projects(client: TestClient) -> None:
    _create_project(client, name="project-a")
    _create_project(client, name="project-b")

    response = client.get("/projects")
    assert response.status_code == 200
    names = {project["name"] for project in response.json()}
    assert names == {"project-a", "project-b"}


def test_list_projects_includes_latest_score_and_certification(
    client: TestClient, db_session: Session
) -> None:
    project = _create_project(client)
    without_assessment = _create_project(client, name="never-assessed")

    now = datetime.now(UTC)
    # Inserted out of chronological order on purpose: the older, higher-scoring
    # assessment is added last, so a bug that picks "last row seen" instead of
    # "most recent created_at" would report the wrong one here.
    newer = AssessmentModel(
        project_id=project["id"],
        version="v2",
        status="COMPLETED",
        trust_score=95,
        certification_level="HIGH_TRUST",
        created_at=now,
    )
    older = AssessmentModel(
        project_id=project["id"],
        version="v1",
        status="COMPLETED",
        trust_score=10,
        certification_level="BLOCKED",
        created_at=now - timedelta(hours=1),
    )
    db_session.add_all([older, newer])
    db_session.commit()

    projects_by_id = {p["id"]: p for p in client.get("/projects").json()}

    assert projects_by_id[project["id"]]["latest_trust_score"] == 95
    assert projects_by_id[project["id"]]["latest_certification_level"] == "HIGH_TRUST"
    assert projects_by_id[without_assessment["id"]]["latest_trust_score"] is None
    assert projects_by_id[without_assessment["id"]]["latest_certification_level"] is None


def test_get_project(client: TestClient) -> None:
    created = _create_project(client)

    response = client.get(f"/projects/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_project_not_found(client: TestClient) -> None:
    response = client.get("/projects/does-not-exist")
    assert response.status_code == 404


def test_update_project(client: TestClient) -> None:
    created = _create_project(client)

    response = client.patch(f"/projects/{created['id']}", json={"name": "renamed"})
    assert response.status_code == 200
    assert response.json()["name"] == "renamed"
    assert response.json()["repository_url"] == created["repository_url"]


def test_update_project_subdirectory(client: TestClient) -> None:
    created = _create_project(client)
    assert created["subdirectory"] is None

    response = client.patch(f"/projects/{created['id']}", json={"subdirectory": "backend"})
    assert response.status_code == 200
    assert response.json()["subdirectory"] == "backend"


def test_update_project_not_found(client: TestClient) -> None:
    response = client.patch("/projects/does-not-exist", json={"name": "x"})
    assert response.status_code == 404


def test_delete_project(client: TestClient) -> None:
    created = _create_project(client)

    response = client.delete(f"/projects/{created['id']}")
    assert response.status_code == 204

    response = client.get(f"/projects/{created['id']}")
    assert response.status_code == 404


def test_delete_project_not_found(client: TestClient) -> None:
    response = client.delete("/projects/does-not-exist")
    assert response.status_code == 404
