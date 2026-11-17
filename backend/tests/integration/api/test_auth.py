def test_register_works_and_returns_a_token(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"first_name": "Ulrich", "last_name": "Ulrichson", "email": "ulli@ullrich.de", "password": "1234567acht"},
    )
    assert response.status_code == 201
    assert response.json()["access_token"] is not None
    assert response.json()["token_type"] == "bearer"


def test_duplicate_email_gives_409(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"first_name": "Ulrich", "last_name": "Ulrichson", "email": "ulli@ullrich.de", "password": "1234567acht"},
    )
    assert response.status_code == 201
    response2 = client.post(
        "/api/v1/auth/register",
        json={"first_name": "Ulla", "last_name": "Ullason", "email": "ulli@ullrich.de", "password": "123456sieben8"},
    )
    assert response2.status_code == 409


def test_password_thats_too_short_gives_422(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"first_name": "Arnold", "last_name": "Arnoldson", "email": "Arne@Arnold.de", "password": "123"},
    )
    assert response.status_code == 422


def test_successful_login_returns_token(client, registered_user):
    login_response = client.post(
        "/api/v1/auth/token", json={"email": registered_user["email"], "password": registered_user["password"]}
    )
    assert login_response.status_code == 200
    assert login_response.json()["access_token"] is not None
    assert login_response.json()["token_type"] == "bearer"


def test_wrong_password_gives_401(client, registered_user):
    login_response = client.post(
        "/api/v1/auth/token", json={"email": registered_user["email"], "password": "very-wrong-pw"}
    )
    assert login_response.status_code == 401


def test_unknown_email_gives_401(client, registered_user):
    login_response = client.post(
        "/api/v1/auth/token", json={"email": "verywrong@email.xy", "password": registered_user["password"]}
    )
    assert login_response.status_code == 401
