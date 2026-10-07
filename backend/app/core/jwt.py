from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import settings
from app.domain.user import Role, User

_ALGORITHM = "HS256"
_ACCESS_TOKEN_TTL = timedelta(hours=8)


def create_access_token(user: User) -> str:
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role.value,
        "exp": datetime.now(UTC) + _ACCESS_TOKEN_TTL,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=_ALGORITHM)


class TokenPayload:
    def __init__(self, user_id: str, email: str, role: Role) -> None:
        self.user_id = user_id
        self.email = email
        self.role = role


def decode_access_token(token: str) -> TokenPayload | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[_ALGORITHM])
    except jwt.InvalidTokenError:
        return None
    return TokenPayload(user_id=payload["sub"], email=payload["email"], role=Role(payload["role"]))
