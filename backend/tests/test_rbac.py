from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.application.user_service import UserService
from app.domain.user import Role
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from app.main import app


@pytest.fixture()
def bare_client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def _create_user(db_session: Session, email: str, password: str, role: Role) -> None:
    UserService(SqlAlchemyUserRepository(db_session)).create(email, password, role)


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_login_with_valid_credentials_returns_token(
    bare_client: TestClient, db_session: Session
) -> None:
    _create_user(db_session, "admin@example.com", "s3cret-pw", Role.ADMIN)
    response = bare_client.post(
        "/auth/login", json={"email": "admin@example.com", "password": "s3cret-pw"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_with_wrong_password_is_rejected(
    bare_client: TestClient, db_session: Session
) -> None:
    _create_user(db_session, "admin@example.com", "s3cret-pw", Role.ADMIN)
    response = bare_client.post(
        "/auth/login", json={"email": "admin@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_login_with_unknown_email_is_rejected(bare_client: TestClient) -> None:
    response = bare_client.post(
        "/auth/login", json={"email": "nobody@example.com", "password": "whatever"}
    )
    assert response.status_code == 401


def test_viewer_can_read_but_not_write(bare_client: TestClient, db_session: Session) -> None:
    _create_user(db_session, "viewer@example.com", "s3cret-pw", Role.VIEWER)
    token = _login(bare_client, "viewer@example.com", "s3cret-pw")
    headers = {"Authorization": f"Bearer {token}"}

    read_response = bare_client.get("/projects", headers=headers)
    assert read_response.status_code == 200

    write_response = bare_client.post(
        "/projects",
        json={"name": "p", "repository_url": "https://x"},
        headers=headers,
    )
    assert write_response.status_code == 403


def test_admin_can_read_and_write(bare_client: TestClient, db_session: Session) -> None:
    _create_user(db_session, "admin@example.com", "s3cret-pw", Role.ADMIN)
    token = _login(bare_client, "admin@example.com", "s3cret-pw")
    headers = {"Authorization": f"Bearer {token}"}

    write_response = bare_client.post(
        "/projects",
        json={"name": "p", "repository_url": "https://x"},
        headers=headers,
    )
    assert write_response.status_code == 201


def test_invalid_jwt_is_rejected(bare_client: TestClient) -> None:
    response = bare_client.get("/projects", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


def test_api_key_still_grants_full_access(bare_client: TestClient, db_session: Session) -> None:
    from app.application.api_key_service import ApiKeyService
    from app.infrastructure.repositories.api_key_repository import SqlAlchemyApiKeyRepository

    _, plaintext_key = ApiKeyService(SqlAlchemyApiKeyRepository(db_session)).create("ci")
    response = bare_client.post(
        "/projects",
        json={"name": "p", "repository_url": "https://x"},
        headers={"X-API-Key": plaintext_key},
    )
    assert response.status_code == 201
