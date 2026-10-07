from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_user_service
from app.api.schemas.auth import LoginRequest, TokenResponse
from app.application.user_service import UserService
from app.core.jwt import create_access_token
from app.domain.user import InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest, service: UserService = Depends(get_user_service)
) -> TokenResponse:
    try:
        user = service.authenticate(payload.email, payload.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return TokenResponse(access_token=create_access_token(user))
