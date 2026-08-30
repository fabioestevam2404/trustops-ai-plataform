from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass
class Project:
    id: str
    name: str
    repository_url: str
    created_at: datetime
    # Subpasta do repositório onde os scanners de qualidade (dependências,
    # pytest, ruff) devem rodar — None/"" significa a raiz do clone, o
    # comportamento original. Scanners de segurança (bandit/semgrep/
    # gitleaks/trivy) sempre varrem o repositório inteiro, independente
    # deste campo: um segredo ou misconfig pode estar em qualquer subpasta
    # de um monorepo, não só na que está sendo avaliada por qualidade.
    subdirectory: str | None = None
    latest_trust_score: int | None = None
    latest_certification_level: str | None = None


class ProjectNotFoundError(Exception):
    def __init__(self, project_id: str) -> None:
        self.project_id = project_id
        super().__init__(f"Project {project_id} not found")


class ProjectRepository(Protocol):
    def create(
        self, name: str, repository_url: str, subdirectory: str | None = None
    ) -> Project: ...

    def get(self, project_id: str) -> Project | None: ...

    def list(self) -> list[Project]: ...

    def update(
        self,
        project_id: str,
        name: str | None,
        repository_url: str | None,
        subdirectory: str | None = None,
    ) -> Project | None: ...

    def delete(self, project_id: str) -> bool: ...
