from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.application.api_key_service import ApiKeyService
from app.domain.api_key import ApiKeyNotFoundError
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.api_key_repository import SqlAlchemyApiKeyRepository
from app.main import app


@pytest.fixture()
def bare_client(db_session: Session) -> Generator[TestClient, None, None]:
    """A TestClient with no API key preset, to exercise auth itself."""

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_protected_route_rejects_missing_key(bare_client: TestClient) -> None:
    response = bare_client.get("/projects")
    assert response.status_code == 401


def test_protected_route_rejects_invalid_key(bare_client: TestClient) -> None:
    response = bare_client.get("/projects", headers={"X-API-Key": "not-a-real-key"})
    assert response.status_code == 401


def test_protected_route_accepts_valid_key(
    bare_client: TestClient, db_session: Session
) -> None:
    _, plaintext_key = ApiKeyService(SqlAlchemyApiKeyRepository(db_session)).create("ci")
    response = bare_client.get("/projects", headers={"X-API-Key": plaintext_key})
    assert response.status_code == 200


def test_revoked_key_is_rejected(bare_client: TestClient, db_session: Session) -> None:
    service = ApiKeyService(SqlAlchemyApiKeyRepository(db_session))
    api_key, plaintext_key = service.create("short-lived")
    service.revoke(api_key.id)

    response = bare_client.get("/projects", headers={"X-API-Key": plaintext_key})
    assert response.status_code == 401


def test_health_does_not_require_a_key(bare_client: TestClient) -> None:
    response = bare_client.get("/health")
    assert response.status_code == 200


def test_metrics_does_not_require_a_key(bare_client: TestClient) -> None:
    response = bare_client.get("/metrics")
    assert response.status_code == 200


def test_revoking_unknown_key_raises(db_session: Session) -> None:
    service = ApiKeyService(SqlAlchemyApiKeyRepository(db_session))
    with pytest.raises(ApiKeyNotFoundError):
        service.revoke("does-not-exist")
