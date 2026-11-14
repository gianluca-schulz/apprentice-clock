from bcrypt import checkpw, gensalt, hashpw


def hash_password(password: str) -> str:
    text_bit = password.encode()
    text_hashed = hashpw(text_bit, gensalt()).decode()
    return text_hashed


def verify_password(password: str, hashed_password: str) -> bool:
    return checkpw(password.encode(), hashed_password.encode())
