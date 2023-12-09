from typing import Optional

from fastapi import Depends

from app.domain.user.entity import UserInUpdate, UserInDB, User
from app.infra.database.models.user import UserModel
from app.infra.user.user_repository import UserRepository
from app.shared import request_object, use_case, response_object


class UpdateUserRequestObject(request_object.ValidRequestObject):
    def __init__(self, id: str, obj_in: UserInUpdate) -> None:
        self.id = id
        self.obj_in = obj_in

    @classmethod
    def builder(cls, id: str, payload: UserInUpdate) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if id is None:
            invalid_req.add_error("id", "Invalid user id")

        if payload is None:
            invalid_req.add_error("payload", "Invalid payload")

        if invalid_req.has_errors():
            return invalid_req

        return UpdateUserRequestObject(id=id, obj_in=payload)


class UpdateUserUseCase(use_case.UseCase):
    def __init__(self, user_repository: UserRepository = Depends(UserRepository)):
        self.user_repository = user_repository

    def process_request(self, req_object: UpdateUserRequestObject):
        user: Optional[UserModel] = self.user_repository.get_by_id(req_object.id)
        if not user:
            return response_object.ResponseFailure.build_not_found_error("User does not exist")

        self.user_repository.update(id=user.id, data=req_object.obj_in)
        user.reload()
        return User(**UserInDB.model_validate(user).model_dump())
