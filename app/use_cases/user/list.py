import math
from typing import Optional, List

from app.domain.shared.entity import Pagination
from app.domain.user.entity import ManyUserResponse, UserInDB, User
from app.infra.database.models.user import UserModel
from app.infra.user.user_repository import UserRepository
from app.shared import request_object, use_case
from fastapi import Depends


class ListUserRequestObject(request_object.ValidRequestObject):
    def __init__(self, page_index: int = 1, page_size: int = 20):
        self.page_index = page_index
        self.page_size = page_size

    @classmethod
    def builder(cls, page_index: int = 1, page_size: int = 20):
        return ListUserRequestObject(page_index=page_index, page_size=page_size)


class ListUserUseCase(use_case.UseCase):
    def __init__(self, user_repository: UserRepository = Depends(UserRepository)):
        self.user_repository = user_repository

    def process_request(self, req_object: ListUserRequestObject):
        users: Optional[List[UserModel]] = self.user_repository.list(page_size=req_object.page_size,
                                                                     page_index=req_object.page_index)

        total = self.user_repository.count()

        return ManyUserResponse(pagination=Pagination(total=total,
                                                      page_index=req_object.page_index,
                                                      total_pages=math.ceil(total / req_object.page_size)),
                                data=[User(**UserInDB.model_validate(user).model_dump()) for user in users])
