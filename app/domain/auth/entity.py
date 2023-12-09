from typing import Optional

from pydantic import BaseModel, field_validator, EmailStr

from app.domain.shared.entity import BaseEntity
from app.domain.user.entity import User


class Token(BaseModel):
    access_token: Optional[str] = None


class TokenData(BaseModel):
    email: str
    id: str = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(LoginRequest):
    fullname: str

    @field_validator("password")
    def validate_min_length(cls, value):
        if len(value) < 8:
            raise ValueError(f"Password must be at least 8 characters")
        return value


class AuthInfoInResponse(BaseEntity, Token):
    user: User
