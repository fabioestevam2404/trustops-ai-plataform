from pathlib import Path

from fastapi.testclient import TestClient


def _create_project(client: TestClient, repo_path: Path) -> dict:
    response = client.post(
        "/projects",
        json={"name": "demo", "repository_url": str(repo_path)},
    )
    assert response.status_code == 201
    return response.json()


def test_certificate_issued_automatically_when_blocked(
    client: TestClient, demo_repo_path: Path
) -> None:
    project = _create_project(client, demo_repo_path)
    assessment = client.post(f"/projects/{project['id']}/assessments", json={}).json()
    assert assessment["certification_level"] == "BLOCKED"

    response = client.get(f"/assessments/{assessment['id']}/certificate")
    assert response.status_code == 200
    certificate = response.json()
    assert certificate["assessment_id"] == assessment["id"]
    assert certificate["project_id"] == project["id"]
    assert certificate["certification_level"] == "BLOCKED"
    assert certificate["status"] == "ISSUED"


def test_certificate_issued_automatically_when_approved(
    client: TestClient, clean_repo_path: Path
) -> None:
    project = _create_project(client, clean_repo_path)
    assessment = client.post(f"/projects/{project['id']}/assessments", json={}).json()
    assert assessment["certification_level"] != "BLOCKED"

    certificate = client.get(f"/assessments/{assessment['id']}/certificate").json()
    assert certificate["certification_level"] == assessment["certification_level"]


def test_certificate_not_found_for_unknown_assessment(client: TestClient) -> None:
    response = client.get("/assessments/does-not-exist/certificate")
    assert response.status_code == 404


def test_list_certificates_for_project(client: TestClient, clean_repo_path: Path) -> None:
    project = _create_project(client, clean_repo_path)
    client.post(f"/projects/{project['id']}/assessments", json={})
    client.post(f"/projects/{project['id']}/assessments", json={})

    response = client.get(f"/projects/{project['id']}/certificates")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_assessment_report_shape(client: TestClient, demo_repo_path: Path) -> None:
    project = _create_project(client, demo_repo_path)
    assessment = client.post(f"/projects/{project['id']}/assessments", json={}).json()

    report = client.get(f"/assessments/{assessment['id']}/report").json()
    assert report["project"] == "demo"
    assert report["version"] == assessment["version"]
    assert report["trust_score"] == assessment["trust_score"]
    assert report["status"] == "BLOCKED"

    findings = client.get(f"/assessments/{assessment['id']}/findings").json()
    critical_count = sum(1 for f in findings if f["severity"] == "CRITICAL")
    assert report["findings_by_severity"]["critical"] == critical_count


def test_risk_register_returns_only_critical_and_high(
    client: TestClient, demo_repo_path: Path
) -> None:
    project = _create_project(client, demo_repo_path)
    client.post(f"/projects/{project['id']}/assessments", json={})

    response = client.get(f"/projects/{project['id']}/risk-register")
    assert response.status_code == 200
    risks = response.json()
    assert len(risks) > 0
    assert all(finding["severity"] in ("CRITICAL", "HIGH") for finding in risks)


def test_risk_register_empty_when_no_completed_assessment(client: TestClient) -> None:
    project = _create_project(client, Path("/tmp/does-not-matter"))
    response = client.get(f"/projects/{project['id']}/risk-register")
    assert response.status_code == 200
    assert response.json() == []
