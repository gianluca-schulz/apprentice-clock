from uuid import uuid4

import jwt
import pytest

from app.core.auth import decode_token, generate_token, hash_password, verify_password


def test_hashed_password_does_not_include_password():
    password: str = "123vierfuenf67"
    hashed_password = hash_password(password)
    assert password != hashed_password
    assert password not in hashed_password


def test_equal_passwords_differnt_hashes():
    password_one = "123vierfuenf67"
    password_two = "123vierfuenf67"
    assert hash_password(password_one) != hash_password(password_two)


def test_verify_password_correct():
    password = "123vierfuenf67"
    hashed_pw = hash_password(password)
    assert verify_password(password, hashed_pw)


def test_verify_password_incorrect():
    password = "123vierfuenf67"
    hashed_pw = hash_password(password)
    assert not verify_password("false-password", hashed_pw)


def test_token_encode_decode_roundtrip():
    secret_key = "wNn5UY6QzYlOHMzXiHaCW7x9_Y_sqifLW9LXQuDaQAU"
    token_expiration_days = 1
    user_id = uuid4()
    token = generate_token(user_id, secret_key, token_expiration_days)
    decoded_token = decode_token(token, secret_key)
    assert user_id == decoded_token.sub
    assert decoded_token.exp is not None


def test_expired_token_raises_error():
    secret_key = "wNn5UY6QzYlOHMzXiHaCW7x9_Y_sqifLW9LXQuDaQAU"
    token_expiration_days = -1
    user_id = uuid4()
    token = generate_token(user_id, secret_key, token_expiration_days)
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(token, secret_key)


def test_tampered_token_raises_error():
    secret_key = "wNn5UY6QzYlOHMzXiHaCW7x9_Y_sqifLW9LXQuDaQAU"
    token_expiration_days = 1
    user_id = uuid4()
    token = generate_token(user_id, secret_key, token_expiration_days)
    user_id2 = uuid4()
    token2 = generate_token(user_id2, secret_key, token_expiration_days)
    header1, _, signature1 = token.split(".")
    _, payload2, _ = token2.split(".")
    tampered_token = f"{header1}.{payload2}.{signature1}"
    with pytest.raises(jwt.InvalidSignatureError):
        decode_token(tampered_token, secret_key)
