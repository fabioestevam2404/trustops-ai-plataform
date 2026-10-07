from sqlalchemy.orm import Session

from app.domain.user import Role, User
from app.infrastructure.db.models import UserModel


def _to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        password_hash=model.password_hash,
        role=Role(model.role),
        created_at=model.created_at,
    )


class SqlAlchemyUserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, email: str, password_hash: str, role: Role) -> User:
        model = UserModel(email=email, password_hash=password_hash, role=role.value)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return _to_entity(model)

    def get_by_email(self, email: str) -> User | None:
        model = self._db.query(UserModel).filter(UserModel.email == email).first()
        return _to_entity(model) if model else None

    def list(self) -> list[User]:
        models = self._db.query(UserModel).order_by(UserModel.created_at.desc()).all()
        return [_to_entity(model) for model in models]
