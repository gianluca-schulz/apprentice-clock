import pytest
from sqlalchemy import select

from app.models.user import User
from app.schemas.auth import RegisterRequest


@pytest.fixture()
def registered_user(client) -> dict[str, str]:
    registration_data = RegisterRequest(
        first_name="Ulrich", last_name="Ulrichson", email="ulli@ullrich.de", password="1234567acht"
    )
    json_registration_data = registration_data.model_dump(mode="json")
    json_registration_data["password"] = registration_data.password.get_secret_value()
    response = client.post("/api/v1/auth/register", json=json_registration_data)
    assert response.status_code == 201
    return json_registration_data


@pytest.fixture()
def access_token(client, registered_user) -> str:
    token_response = client.post(
        "/api/v1/auth/token", json={"email": registered_user["email"], "password": registered_user["password"]}
    )
    assert token_response.status_code == 200
    login_body = token_response.json()
    return login_body["access_token"]


@pytest.fixture()
async def db_user(registered_user, session) -> User:
    user = await session.scalar(select(User).where(User.email == registered_user["email"]))
    assert user is not None
    return user
