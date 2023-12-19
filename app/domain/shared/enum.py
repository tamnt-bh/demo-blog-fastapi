from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class UserRole(str, ExtendedEnum):
    USER = "user"
    ADMIN = "admin"

class Sort(str, ExtendedEnum):
    ASCE = "asce"
    DESC = "desc"
