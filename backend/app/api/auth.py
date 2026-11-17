from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.core.auth import generate_token
from app.database import get_session
from app.dependencies.settings import get_settings
from app.schemas.auth import RegisterRequest, SignInRequest, TokenResponse
from app.services.auth import EmailAlreadyExistsError, InvalidCredentialsError, authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def post_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    request: RegisterRequest,
) -> TokenResponse:
    try:
        user = await register_user(session, request)
    except EmailAlreadyExistsError:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="registration failed")
    return TokenResponse(access_token=generate_token(user.id, settings.secret_key, settings.token_expiration_days))


@router.post("/token", status_code=status.HTTP_200_OK)
async def post_token(
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    request: SignInRequest,
) -> TokenResponse:
    try:
        user = await authenticate_user(session=session, body=request)
    except InvalidCredentialsError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    return TokenResponse(access_token=generate_token(user.id, settings.secret_key, settings.token_expiration_days))
