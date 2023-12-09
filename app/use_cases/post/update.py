from typing import Optional

from bson import ObjectId
from fastapi import Depends

from app.domain.post.entity import Post, PostInDB, PostInUpdate
from app.domain.user.entity import User, UserInDB
from app.infra.post.post_repository import PostRepository
from app.shared import request_object, use_case, response_object


class UpdatePostObjectRequest(request_object.ValidRequestObject):
    def __init__(self, post_id: str, payload: PostInUpdate, author_id: Optional[str],
                 is_admin: Optional[bool] = False):
        self.post_id = post_id
        self.author_id = author_id
        self.is_admin = is_admin
        self.payload = payload

    @classmethod
    def builder(cls, post_id: str, payload: PostInUpdate, author_id: Optional[str],
                is_admin: Optional[bool] = False) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if not post_id:
            invalid_req.add_error("post_id", "Invalid ID")

        if not author_id and not is_admin:
            invalid_req.add_error("permission", "Do not have permission to update")

        if invalid_req.has_errors():
            return invalid_req
        return UpdatePostObjectRequest(post_id=post_id, author_id=author_id, is_admin=is_admin, payload=payload)


class UpdatePostUseCase(use_case.UseCase):
    def __init__(self, post_repository: PostRepository = Depends(PostRepository)):
        self.post_repository = post_repository

    def process_request(self, req_object: UpdatePostObjectRequest):
        if req_object.is_admin:
            post = self.post_repository.find_one({"_id": ObjectId(req_object.post_id)})
        else:
            post = self.post_repository.find_one(
                {"_id": ObjectId(req_object.post_id), "author": ObjectId(req_object.author_id)})

        if not post:
            return response_object.ResponseFailure.build_not_found_error(message="Post does not exist.")

        self.post_repository.update(id=post.id, data=req_object.payload)
        post.reload()

        return Post(**PostInDB.model_validate(post).model_dump(exclude=({"author"})),
                    author=User(**UserInDB.model_validate(post.author).model_dump()))
