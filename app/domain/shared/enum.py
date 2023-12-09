from enum import Enum


class _ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class UserRole(str, _ExtendedEnum):
    USER = "user"
    ADMIN = "admin"
