import subprocess
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.infrastructure.db.models import Base
from app.infrastructure.db.session import get_db
from app.main import app


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _isolate_evidence_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "evidence_store_path", str(tmp_path / "evidence"))


def _commit_repo(repo: Path) -> None:
    subprocess.run(["git", "init", "--quiet", "--initial-branch=main"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=test@trustops.local",
            "-c",
            "user.name=trustops-test",
            "commit",
            "--quiet",
            "-m",
            "initial commit",
        ],
        cwd=repo,
        check=True,
    )


def _write_clean_files(repo: Path) -> None:
    (repo / "app.py").write_text(
        "def add(a: int, b: int) -> int:\n    return a + b\n",
        encoding="utf-8",
    )
    (repo / "test_app.py").write_text(
        "from app import add\n\n\ndef test_add() -> None:\n    assert add(1, 2) == 3\n",
        encoding="utf-8",
    )


@pytest.fixture()
def demo_repo_path(tmp_path: Path) -> Path:
    """Local git repo with a real quality issue (unused import) and a synthetic
    secret/vulnerability pattern — no network needed for tests."""
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    (repo / "app.py").write_text(
        "import os\n\n\ndef add(a: int, b: int) -> int:\n    return a + b\n",
        encoding="utf-8",
    )
    (repo / "test_app.py").write_text(
        "from app import add\n\n\ndef test_add() -> None:\n    assert add(1, 2) == 3\n",
        encoding="utf-8",
    )
    # Synthetic, obviously-fake secrets/patterns to exercise the security scanners
    # (Bandit, Semgrep, Gitleaks, Trivy) — never real credentials.
    (repo / "insecure.py").write_text(
        "import subprocess\n\n"
        'AWS_ACCESS_KEY_ID = "AKIAABCDEFGHIJKLMNOP"\n\n\n'
        "def run(cmd: str) -> None:\n"
        "    subprocess.run(cmd, shell=True)\n\n\n"
        "def danger(expr: str):\n"
        "    return eval(expr)\n",
        encoding="utf-8",
    )
    _commit_repo(repo)
    return repo


@pytest.fixture()
def clean_repo_path(tmp_path: Path) -> Path:
    """Local git repo with no quality or security issues — used to exercise the
    non-blocked certification path (demo_repo_path always yields BLOCKED)."""
    repo = tmp_path / "clean-repo"
    repo.mkdir()
    _write_clean_files(repo)
    _commit_repo(repo)
    return repo
