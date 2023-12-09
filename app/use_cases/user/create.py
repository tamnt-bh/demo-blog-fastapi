from builtins import Exception

from fastapi import Depends
from mongoengine import NotUniqueError

from app.domain.user.entity import User, UserInCreate, UserInDB
from app.infra.database.models.user import UserModel
from app.infra.security.security_service import get_password_hash
from app.infra.user.user_repository import UserRepository
from app.shared import request_object, use_case, response_object


class CreateUserRequestObject(request_object.ValidRequestObject):
    def __init__(self, user_in: UserInCreate) -> None:
        self.user_in = user_in

    @classmethod
    def builder(cls, payload: UserInCreate) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()

        if payload is None:
            invalid_req.add_error("payload", "Invalid payload")

        if not payload.email:
            invalid_req.add_error("payload.email", "Invalid email")

        if invalid_req.has_errors():
            return invalid_req

        return CreateUserRequestObject(user_in=payload)


class CreateUserUseCase(use_case.UseCase):
    def __init__(self, user_repository: UserRepository = Depends(UserRepository)):
        self.user_repository = user_repository

    def process_request(self, req_object: CreateUserRequestObject):
        user_in: UserInCreate = req_object.user_in

        obj_in: UserInCreate = UserInCreate(
            **user_in.model_dump(exclude={"password"}), password=get_password_hash(password=user_in.password)
        )
        try:
            user: UserModel = self.user_repository.create(user=obj_in)
            return User(**UserInDB.model_validate(user).model_dump())
        except NotUniqueError:
            return response_object.ResponseFailure.build_system_error("This email existed already")
        except Exception:
            return response_object.ResponseFailure.build_system_error("Something went error.")
