from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth import TokenData, decode_token
from app.dependencies.database import CurrentSession
from app.dependencies.settings import CurrentSettings
from app.models.user import User

bearer = HTTPBearer(auto_error=False)
INVALID_TOKEN_DETAIL = "invalid credentials"


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    session: CurrentSession,
    settings: CurrentSettings,
) -> User:

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
    try:
        token_data: TokenData = decode_token(credentials.credentials, settings.secret_key)
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_TOKEN_DETAIL) from None
    user = await session.get(User, token_data.sub)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_TOKEN_DETAIL)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
