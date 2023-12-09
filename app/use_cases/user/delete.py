from typing import Optional

from fastapi import Depends

from app.infra.database.models.user import UserModel
from app.infra.user.user_repository import UserRepository
from app.shared import request_object, response_object, use_case


class DeleteUserRequestObject(request_object.ValidRequestObject):
    def __init__(self, user_id: str):
        self.user_id = user_id

    @classmethod
    def builder(cls, user_id: str) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if not user_id:
            invalid_req.add_error("id", "Invalid ID")

        if invalid_req.has_errors():
            return invalid_req

        return DeleteUserRequestObject(user_id=user_id)


class DeleteUserUseCase(use_case.UseCase):
    def __init__(self, user_repository: UserRepository = Depends(UserRepository)):
        self.user_repository = user_repository

    def process_request(self, req_object: DeleteUserRequestObject):
        user: Optional[UserModel] = self.user_repository.get_by_id(user_id=req_object.user_id)
        if not user:
            return response_object.ResponseFailure.build_not_found_error(message="User does not exist.")

        try:
            self.user_repository.delete(user.id)
            return {"success": True}
        except Exception:
            return response_object.ResponseFailure.build_system_error("Something went error.")
