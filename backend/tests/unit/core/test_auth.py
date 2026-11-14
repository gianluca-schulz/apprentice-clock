from app.core.auth import hash_password, verify_password


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
