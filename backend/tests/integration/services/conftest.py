import pytest

from app.schemas.auth import RegisterRequest
from app.services.auth import register_user


@pytest.fixture()
async def registered_user(session) -> RegisterRequest:
    body = RegisterRequest(
        first_name="Testuser", last_name="lastnameuser", password="testpassword", email="test@user.de"
    )
    await register_user(session=session, body=body)
    return body
