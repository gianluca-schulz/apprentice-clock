import pytest
from pydantic import ValidationError

from app.schemas.auth import RegisterRequest, SignInRequest


@pytest.mark.parametrize(
    ("first_name", "last_name", "email", "password"),
    [
        ("Max", "Mustermann", "max@example.de", "password"),
        ("A", "B", "a@b.de", "12345678"),
        ("a" * 32, "a" * 32, "test@email.de", "password"),
        ("Anna-Lena", "Müller", "anna.lena@example.de", "correct horse battery"),
        ("fvan der", "Berg", "vdb@example.de", "8chars!!"),
        ("Max", "Mustermann", "Test@Email.DE", "password"),
    ],
)
def test_register_request_valid(first_name, last_name, email, password):
    request = RegisterRequest(first_name=first_name, last_name=last_name, password=password, email=email)
    assert request.first_name == first_name.strip()
    assert request.last_name == last_name.strip()
    assert request.email == email.strip().lower()
    assert request.password.get_secret_value() == password


@pytest.mark.parametrize(
    ("first_name", "last_name", "email", "password", "field"),
    [
        ("", "Mustermann", "max@example.de", "password", "first_name"),
        ("   ", "Mustermann", "max@example.de", "password", "first_name"),
        ("a" * 33, "Mustermann", "max@example.de", "password", "first_name"),
        ("Max", "", "max@example.de", "password", "last_name"),
        ("Max", "   ", "max@example.de", "password", "last_name"),
        ("Max", "a" * 33, "max@example.de", "password", "last_name"),
        ("Max", "Mustermann", "no-at-sign", "password", "email"),
        ("Max", "Mustermann", "a@", "password", "email"),
        ("Max", "Mustermann", "@b.de", "password", "email"),
        ("Max", "Mustermann", "", "password", "email"),
        ("Max", "Mustermann", "a b@c.de", "password", "email"),
        ("Max", "Mustermann", "max@example.de", "a" * 7, "password"),
        ("Max", "Mustermann", "max@example.de", "", "password"),
        ("Max", "Mustermann", "max@example.de", "a" * 33, "password"),
    ],
)
def test_register_request_invalid(first_name, last_name, email, password, field):
    with pytest.raises(ValidationError) as excinfo:
        RegisterRequest(first_name=first_name, last_name=last_name, password=password, email=email)
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"][0] == field


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("max@example.de", "password"),
        ("a@b.de", "12345678"),
        ("test@email.de", "password"),
        ("anna.lena@example.de", "correct horse battery"),
        ("vdb@example.de", "8chars!!"),
        ("Test@Email.DE", "password"),
    ],
)
def test_signin_request_valid(email, password):
    request = SignInRequest(email=email, password=password)
    assert request.email == email.lower().strip()
    assert request.password == password


@pytest.mark.parametrize(
    "email",
    [
        "no-at-sign",
        "a@",
        "@b.de",
        "",
        "a b@c.de",
    ],
)
def test_signin_request_invalid(email):
    with pytest.raises(ValidationError):
        SignInRequest(password="password", email=email)
