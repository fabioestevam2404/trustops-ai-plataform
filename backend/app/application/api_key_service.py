import hashlib
import secrets

from app.domain.api_key import ApiKey, ApiKeyNotFoundError, ApiKeyRepository

_KEY_PREFIX = "tops"


def _hash(plaintext_key: str) -> str:
    return hashlib.sha256(plaintext_key.encode("utf-8")).hexdigest()


class ApiKeyService:
    def __init__(self, repository: ApiKeyRepository) -> None:
        self._repository = repository

    def create(self, name: str) -> tuple[ApiKey, str]:
        """Creates a new key and returns it alongside the plaintext value.

        The plaintext is only ever available here, at creation time — only its
        hash is persisted, so it cannot be recovered afterwards.
        """
        plaintext_key = f"{_KEY_PREFIX}_{secrets.token_urlsafe(32)}"
        api_key = self._repository.create(name, _hash(plaintext_key))
        return api_key, plaintext_key

    def authenticate(self, plaintext_key: str) -> ApiKey | None:
        api_key = self._repository.get_by_hash(_hash(plaintext_key))
        if api_key is None or api_key.is_revoked:
            return None
        return api_key

    def list(self) -> list[ApiKey]:
        return self._repository.list()

    def revoke(self, api_key_id: str) -> ApiKey:
        api_key = self._repository.revoke(api_key_id)
        if api_key is None:
            raise ApiKeyNotFoundError(api_key_id)
        return api_key
