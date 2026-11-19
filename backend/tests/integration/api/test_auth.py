from datetime import UTC, datetime, timedelta

import jwt


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


def test_valid_token_returns_user_response(client, registered_user, access_token):
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["first_name"] == registered_user["first_name"]
    assert body["last_name"] == registered_user["last_name"]
    assert body["email"] == registered_user["email"]
    assert "password_hash" not in body


def test_no_token_returns_401_and_authentication_required_message(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    body = response.json()
    assert body["detail"] == "authentication required"


def test_malformed_token_returns_401_and_invalid_credentials_message(client):
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer malformed.test.token"})
    assert response.status_code == 401
    body = response.json()
    assert body["detail"] == "invalid credentials"


async def test_expired_token_returns_401_and_invalid_credentials_message(client, app_settings, db_user):
    secret_key = app_settings.secret_key
    user_id = str(db_user.id)
    payload = {"sub": user_id, "exp": datetime.now(UTC) - timedelta(seconds=10)}
    token = jwt.encode(payload=payload, key=secret_key, algorithm="HS256")
    header = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=header)
    assert response.status_code == 401
    body = response.json()
    assert body["detail"] == "invalid credentials"


async def test_deleted_user_gives_401_and_invalid_credentials_message(client, session, access_token, db_user):
    await session.delete(db_user)
    await session.commit()
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 401
    body = response.json()
    assert body["detail"] == "invalid credentials"
