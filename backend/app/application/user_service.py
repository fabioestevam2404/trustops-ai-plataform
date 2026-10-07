from app.core.passwords import hash_password, verify_password
from app.domain.user import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    Role,
    User,
    UserRepository,
)


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def create(self, email: str, password: str, role: Role) -> User:
        if self._repository.get_by_email(email) is not None:
            raise EmailAlreadyExistsError(email)
        return self._repository.create(email, hash_password(password), role)

    def authenticate(self, email: str, password: str) -> User:
        user = self._repository.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        return user

    def list(self) -> list[User]:
        return self._repository.list()
