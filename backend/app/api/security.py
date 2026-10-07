from fastapi import Depends, Header, HTTPException, status

from app.api.dependencies import get_api_key_service
from app.application.api_key_service import ApiKeyService
from app.domain.api_key import ApiKey

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Missing or invalid API key",
    headers={"WWW-Authenticate": "ApiKey"},
)


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    service: ApiKeyService = Depends(get_api_key_service),
) -> ApiKey:
    if not x_api_key:
        raise _UNAUTHORIZED
    api_key = service.authenticate(x_api_key)
    if api_key is None:
        raise _UNAUTHORIZED
    return api_key
