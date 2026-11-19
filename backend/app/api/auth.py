from fastapi import APIRouter, HTTPException, status

from app.core.auth import generate_token
from app.dependencies.auth import CurrentUser
from app.dependencies.database import CurrentSession
from app.dependencies.settings import CurrentSettings
from app.schemas.auth import RegisterRequest, SignInRequest, TokenResponse, UserResponse
from app.services.auth import EmailAlreadyExistsError, InvalidCredentialsError, authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def post_user(
    session: CurrentSession,
    settings: CurrentSettings,
    body: RegisterRequest,
) -> TokenResponse:
    try:
        user = await register_user(session, body)
    except EmailAlreadyExistsError:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="registration failed")
    return TokenResponse(access_token=generate_token(user.id, settings.secret_key, settings.token_expiration_days))


@router.post("/token", status_code=status.HTTP_200_OK)
async def post_token(
    session: CurrentSession,
    settings: CurrentSettings,
    body: SignInRequest,
) -> TokenResponse:
    try:
        user = await authenticate_user(session=session, body=body)
    except InvalidCredentialsError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    return TokenResponse(access_token=generate_token(user.id, settings.secret_key, settings.token_expiration_days))


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_me(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user)
