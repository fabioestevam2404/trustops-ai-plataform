from fastapi.testclient import TestClient


def _create_project(client: TestClient, name: str = "example-api") -> dict:
    response = client.post(
        "/projects",
        json={"name": name, "repository_url": "https://github.com/org/example-api"},
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
