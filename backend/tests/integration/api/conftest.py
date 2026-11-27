from dataclasses import dataclass
from uuid import UUID

import pytest

from app.core.auth import decode_token


@dataclass
class RegisteredUser:
    id: UUID
    first_name: str
    last_name: str
    email: str
    password: str
    access_token: str


@pytest.fixture()
def registered_user(client, app_settings) -> RegisteredUser:
    register_data = {
        "first_name": "Ulrich",
        "last_name": "Ulrichson",
        "email": "ulrich@son.com",
        "password": "ullisooohn123987",
    }
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    access_token = response.json()["access_token"]
    token_data = decode_token(access_token, app_settings.secret_key)
    return RegisteredUser(
        id=token_data.sub,
        first_name=register_data["first_name"],
        last_name=register_data["last_name"],
        email=register_data["email"],
        password=register_data["password"],
        access_token=access_token,
    )


@pytest.fixture()
def auth_header(registered_user) -> dict[str, str]:
    return {"Authorization": f"Bearer {registered_user.access_token}"}


@pytest.fixture()
def second_registered_user(client, app_settings) -> RegisteredUser:
    register_data = {
        "first_name": "Thorsten",
        "last_name": "Thorstenson",
        "email": "thorsten@son.com",
        "password": "torstenson123987",
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    assert register_response.status_code == 201
    access_token = register_response.json()["access_token"]
    token_data = decode_token(access_token, app_settings.secret_key)
    return RegisteredUser(
        id=token_data.sub,
        first_name=register_data["first_name"],
        last_name=register_data["last_name"],
        email=register_data["email"],
        password=register_data["password"],
        access_token=access_token,
    )


@pytest.fixture()
def second_auth_header(second_registered_user) -> dict[str, str]:
    return {"Authorization": f"Bearer {second_registered_user.access_token}"}


@pytest.fixture()
def created_report(client, auth_header) -> dict[str, str]:
    response = client.post(
        "/api/v1/reports",
        json={"date": "2026-11-26", "title": "splitting wood", "description": "i chopped"},
        headers=auth_header,
    )
    assert response.status_code == 201
    return response.json()
