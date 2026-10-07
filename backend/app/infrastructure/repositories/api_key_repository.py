from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.domain.api_key import ApiKey
from app.infrastructure.db.models import ApiKeyModel


def _to_entity(model: ApiKeyModel) -> ApiKey:
    return ApiKey(
        id=model.id,
        name=model.name,
        key_hash=model.key_hash,
        created_at=model.created_at,
        revoked_at=model.revoked_at,
    )


class SqlAlchemyApiKeyRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, name: str, key_hash: str) -> ApiKey:
        model = ApiKeyModel(name=name, key_hash=key_hash)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return _to_entity(model)

    def get_by_hash(self, key_hash: str) -> ApiKey | None:
        model = self._db.query(ApiKeyModel).filter(ApiKeyModel.key_hash == key_hash).first()
        return _to_entity(model) if model else None

    def list(self) -> list[ApiKey]:
        models = self._db.query(ApiKeyModel).order_by(ApiKeyModel.created_at.desc()).all()
        return [_to_entity(model) for model in models]

    def revoke(self, api_key_id: str) -> ApiKey | None:
        model = self._db.get(ApiKeyModel, api_key_id)
        if model is None:
            return None
        model.revoked_at = datetime.now(UTC)
        self._db.commit()
        self._db.refresh(model)
        return _to_entity(model)
