import pytest

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
