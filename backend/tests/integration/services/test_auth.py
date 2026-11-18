from datetime import datetime

import pytest

from app.core.auth import verify_password
from app.schemas.auth import RegisterRequest, SignInRequest
from app.services.auth import EmailAlreadyExistsError, InvalidCredentialsError, authenticate_user, register_user


async def test_register_user(session):
    body = RegisterRequest(
        first_name="Testuser", last_name="lastnameuser", password="testpassword", email="Test@user.de"
    )
    user = await register_user(session=session, body=body)
    assert user.email == body.email
    assert user.first_name == body.first_name
    assert user.last_name == body.last_name
    assert verify_password(body.password.get_secret_value(), user.password_hash)
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)
    assert user.email_confirmed_at is None


async def test_authenticate_user_with_different_email_casing(session):
    body = RegisterRequest(
        first_name="Testuser", last_name="lastnameuser", password="testpassword", email="TEST@USER.DE"
    )
    user = await register_user(session=session, body=body)
    sign_in_body = SignInRequest(email=body.email, password=body.password.get_secret_value())
    user = await authenticate_user(session=session, body=sign_in_body)
    assert user.email == body.email


async def test_register_user_duplicate_email(session, registered_user):
    body = RegisterRequest(
        first_name="Testuser",
        last_name="lastnameuser",
        password="testpassword",
        email=registered_user.email.capitalize(),
    )
    with pytest.raises(EmailAlreadyExistsError):
        await register_user(session=session, body=body)


async def test_authenticate_user(session, registered_user):
    sign_in_body = SignInRequest(email=registered_user.email, password=registered_user.password.get_secret_value())
    user = await authenticate_user(session=session, body=sign_in_body)
    assert user.email == registered_user.email


async def test_authenticate_user_not_found(session):
    sign_in_body = SignInRequest(email="test@email.com", password="testpassword")
    with pytest.raises(InvalidCredentialsError):
        await authenticate_user(session=session, body=sign_in_body)


async def test_authenticate_user_wrong_pw_raises_error(session, registered_user):
    sign_in_body = SignInRequest(email=registered_user.email, password="wrongpassword")
    with pytest.raises(InvalidCredentialsError):
        await authenticate_user(session=session, body=sign_in_body)


async def test_authenticate_user_invalid_pw_raises_error(session, registered_user):
    sign_in_body = SignInRequest(email=registered_user.email, password="a" * 100)
    with pytest.raises(InvalidCredentialsError):
        await authenticate_user(session=session, body=sign_in_body)
