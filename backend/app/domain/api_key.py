from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass
class ApiKey:
    id: str
    name: str
    key_hash: str
    created_at: datetime
    revoked_at: datetime | None = None

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None


class ApiKeyNotFoundError(Exception):
    def __init__(self, api_key_id: str) -> None:
        self.api_key_id = api_key_id
        super().__init__(f"API key {api_key_id} not found")


class ApiKeyRepository(Protocol):
    def create(self, name: str, key_hash: str) -> ApiKey: ...

    def get_by_hash(self, key_hash: str) -> ApiKey | None: ...

    def list(self) -> list[ApiKey]: ...

    def revoke(self, api_key_id: str) -> ApiKey | None: ...
