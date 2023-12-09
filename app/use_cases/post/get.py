from typing import Optional

from fastapi import Depends

from app.domain.post.entity import Post, PostInDB
from app.domain.user.entity import User, UserInDB
from app.infra.database.models.post import PostModel
from app.infra.post.post_repository import PostRepository
from app.shared import request_object, use_case, response_object


class GetPostByIdObjectRequest(request_object.ValidRequestObject):
    def __init__(self, post_id: str):
        self.post_id = post_id

    @classmethod
    def builder(cls, post_id: str) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if not id:
            invalid_req.add_error("id", "Invalid ID")

        if invalid_req.has_errors():
            return invalid_req
        return GetPostByIdObjectRequest(post_id=post_id)


class GetPostByIdUseCase(use_case.UseCase):
    def __init__(self, post_repository: PostRepository = Depends(PostRepository)):
        self.post_repository = post_repository

    def process_request(self, req_object: GetPostByIdObjectRequest):
        post: Optional[PostModel] = self.post_repository.get_by_id(post_id=req_object.post_id)
        if not post:
            return response_object.ResponseFailure.build_not_found_error(message="User does not exist.")

        return Post(**PostInDB.model_validate(post).model_dump(exclude=({"author"})),
                    author=User(**UserInDB.model_validate(post.author).model_dump()))
