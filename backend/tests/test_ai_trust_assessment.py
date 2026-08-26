from pathlib import Path

from fastapi.testclient import TestClient


def _create_project(client: TestClient, repo_path: Path) -> dict:
    response = client.post(
        "/projects",
        json={"name": "demo", "repository_url": str(repo_path)},
    )
    assert response.status_code == 201
    return response.json()


def test_ai_trust_score_and_findings_computed_when_dataset_present(
    client: TestClient, ai_repo_path: Path
) -> None:
    project = _create_project(client, ai_repo_path)

    assessment = client.post(f"/projects/{project['id']}/assessments", json={}).json()
    assert assessment["ai_trust_score"] is not None
    assert 0 <= assessment["ai_trust_score"] <= 100

    # a successful prompt injection is CRITICAL and always blocks certification,
    # regardless of the numeric trust_score.
    assert assessment["certification_level"] == "BLOCKED"

    findings = client.get(f"/assessments/{assessment['id']}/findings").json()
    ai_findings = [f for f in findings if f["tool"] == "ai-trust"]
    assert any(
        f["severity"] == "HIGH" and "hallucination" in f["description"] for f in ai_findings
    )
    assert any(
        f["severity"] == "CRITICAL" and "injection" in f["description"] for f in ai_findings
    )
    # the resisted injection entry must not produce a finding
    assert sum(1 for f in ai_findings if f["severity"] == "CRITICAL") == 1

    report = client.get(f"/assessments/{assessment['id']}/reports/ai-trust")
    assert report.status_code == 200


def test_ai_trust_score_is_none_without_dataset(
    client: TestClient, clean_repo_path: Path
) -> None:
    project = _create_project(client, clean_repo_path)

    assessment = client.post(f"/projects/{project['id']}/assessments", json={}).json()
    assert assessment["ai_trust_score"] is None

    findings = client.get(f"/assessments/{assessment['id']}/findings").json()
    assert not any(f["tool"] == "ai-trust" for f in findings)

    # falls back to the original 50/50 quality/security formula (no regression).
    expected_trust_score = round(
        0.5 * assessment["quality_score"] + 0.5 * assessment["security_score"]
    )
    assert assessment["trust_score"] == expected_trust_score
