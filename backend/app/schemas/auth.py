from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, EmailStr, SecretStr, StringConstraints

NameString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=32)]
PasswordString = Annotated[SecretStr, StringConstraints(min_length=8, max_length=32)]
EmailString = Annotated[EmailStr, AfterValidator(str.lower)]


class RegisterRequest(BaseModel):
    first_name: NameString
    last_name: NameString
    email: EmailString
    password: PasswordString


class SignInRequest(BaseModel):
    email: EmailString
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    created_at: datetime
    updated_at: datetime
