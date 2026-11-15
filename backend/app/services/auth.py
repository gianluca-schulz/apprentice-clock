from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import RegisterRequest, SignInRequest


class InvalidCredentialsError(Exception):
    pass


class EmailAlreadyExistsError(Exception):
    pass


async def register_user(session: AsyncSession, body: RegisterRequest) -> User:
    """Inserts a user into the database."""
    user = User(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        password_hash=hash_password(body.password.get_secret_value()),
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise EmailAlreadyExistsError
    await session.refresh(user)
    return user


async def authenticate_user(session: AsyncSession, body: SignInRequest) -> User:
    user = await session.scalar(select(User).where(User.email == body.email))
    if user is None:
        raise InvalidCredentialsError
    try:
        if not verify_password(body.password, user.password_hash):
            raise InvalidCredentialsError
    except ValueError:  # bcrypt will throw ValueError pw is too long
        raise InvalidCredentialsError
    return user
