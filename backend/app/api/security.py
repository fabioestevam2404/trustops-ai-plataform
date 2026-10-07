from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status

from app.api.dependencies import get_api_key_service
from app.application.api_key_service import ApiKeyService
from app.core.jwt import decode_access_token
from app.domain.user import Role

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Missing or invalid credentials",
    headers={"WWW-Authenticate": "ApiKey"},
)
_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Admin role required",
)


@dataclass
class Principal:
    """A request's caller, from either of the two supported auth methods.

    An API key always carries full (admin-equivalent) access — it represents
    a trusted machine client (CI/CD, integrations), not a human with a role.
    A JWT carries the role chosen at login, so it's the only path that can
    ever be a non-admin viewer.
    """

    is_admin: bool
    user_id: str | None = None


def _try_api_key(x_api_key: str | None, service: ApiKeyService) -> Principal | None:
    if not x_api_key:
        return None
    api_key = service.authenticate(x_api_key)
    if api_key is None:
        return None
    return Principal(is_admin=True)


def _try_jwt(authorization: str | None) -> Principal | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ")
    payload = decode_access_token(token)
    if payload is None:
        return None
    return Principal(is_admin=payload.role == Role.ADMIN, user_id=payload.user_id)


def require_authenticated(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None),
    service: ApiKeyService = Depends(get_api_key_service),
) -> Principal:
    principal = _try_api_key(x_api_key, service) or _try_jwt(authorization)
    if principal is None:
        raise _UNAUTHORIZED
    return principal


def require_admin(principal: Principal = Depends(require_authenticated)) -> Principal:
    if not principal.is_admin:
        raise _FORBIDDEN
    return principal
