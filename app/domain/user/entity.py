from typing import Optional, List

from pydantic import EmailStr, ConfigDict, field_validator, BaseModel

from app.domain.shared.entity import BaseEntity, IDModelMixin, Pagination, PayloadWithFile
from app.domain.shared.enum import UserRole


def transform_email(email: str) -> str:
    return email.lower()


class UserBase(BaseEntity):
    email: EmailStr
    role: UserRole = UserRole.USER
    fullname: str
    _extract_email = field_validator("email", mode="before")(transform_email)


class UseBaseWithAvatar(UserBase):
    avatar: Optional[str] = None


class UserInDB(IDModelMixin, UseBaseWithAvatar):
    model_config = ConfigDict(from_attributes=True)
    password: Optional[str]

    def is_admin(self):
        return self.role == UserRole.ADMIN


class UserInCreate(UseBaseWithAvatar):
    password: str


class UserInCreatePayload(UserBase, PayloadWithFile):
    password: str

    @field_validator("password")
    def validate_min_length(cls, value):
        if len(value) < 8:
            raise ValueError(f"Password must be at least 8 characters")
        return value


class UpdatePayload(BaseModel):
    email: Optional[EmailStr] = None
    role: UserRole = UserRole.USER
    fullname: Optional[str] = None


class UserInUpdatePayload(UpdatePayload, PayloadWithFile):
    pass


class UserInUpdate(UpdatePayload):
    avatar: Optional[str] = None


class User(UseBaseWithAvatar):
    id: str


class ManyUserResponse(BaseEntity):
    pagination: Optional[Pagination] = None
    data: Optional[List[User]] = None
