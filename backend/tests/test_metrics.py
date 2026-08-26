from pathlib import Path

from fastapi.testclient import TestClient


def test_metrics_endpoint_exposes_prometheus_format(client: TestClient) -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "python_info" in response.text


def test_metrics_include_assessment_counter_after_a_run(
    client: TestClient, clean_repo_path: Path
) -> None:
    project = client.post(
        "/projects", json={"name": "demo", "repository_url": str(clean_repo_path)}
    ).json()
    client.post(f"/projects/{project['id']}/assessments", json={})

    response = client.get("/metrics")
    assert "trustops_assessments_total" in response.text
    assert "trustops_scanner_duration_seconds" in response.text
