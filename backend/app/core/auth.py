from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from bcrypt import checkpw, gensalt, hashpw
from pydantic import BaseModel


class TokenData(BaseModel):
    sub: UUID
    exp: datetime


def hash_password(password: str) -> str:
    text_bit = password.encode()
    text_hashed = hashpw(text_bit, gensalt()).decode()
    return text_hashed


def verify_password(password: str, hashed_password: str) -> bool:
    return checkpw(password.encode(), hashed_password.encode())


def generate_token(user_id: UUID, secret_key: str, token_expiration_days: int) -> str:
    exp = datetime.now(UTC) + timedelta(days=token_expiration_days)
    token_data = {"sub": str(user_id), "exp": exp}
    return jwt.encode(algorithm="HS256", payload=token_data, key=secret_key)


def decode_token(token: str, secret_key: str) -> TokenData:
    payload = jwt.decode(token, key=secret_key, algorithms=["HS256"])
    return TokenData(**payload)
