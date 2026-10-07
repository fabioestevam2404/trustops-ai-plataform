from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol


class Role(str, Enum):
    ADMIN = "admin"
    VIEWER = "viewer"


@dataclass
class User:
    id: str
    email: str
    password_hash: str
    role: Role
    created_at: datetime


class EmailAlreadyExistsError(Exception):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User with email {email} already exists")


class InvalidCredentialsError(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid email or password")


class UserRepository(Protocol):
    def create(self, email: str, password_hash: str, role: Role) -> User: ...

    def get_by_email(self, email: str) -> User | None: ...

    def list(self) -> list[User]: ...
