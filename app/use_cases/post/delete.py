from typing import Optional

from fastapi import Depends
from bson import ObjectId
from app.infra.post.post_repository import PostRepository
from app.shared import request_object, response_object, use_case


class DeletePostRequestObject(request_object.ValidRequestObject):
    def __init__(self, post_id: str, author_id: Optional[str],
                 is_admin: Optional[bool] = False):
        self.post_id = post_id
        self.author_id = author_id
        self.is_admin = is_admin

    @classmethod
    def builder(cls, post_id: str, author_id: Optional[str],
                is_admin: Optional[bool] = False) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if not post_id:
            invalid_req.add_error("post_id", "Invalid ID")

        if not author_id and not is_admin:
            invalid_req.add_error("permission", "Do not have permission to update")

        if invalid_req.has_errors():
            return invalid_req
        return DeletePostRequestObject(post_id=post_id, author_id=author_id, is_admin=is_admin)


class DeletePostUseCase(use_case.UseCase):
    def __init__(self, post_repository: PostRepository = Depends(PostRepository)):
        self.post_repository = post_repository

    def process_request(self, req_object: DeletePostRequestObject):
        if req_object.is_admin:
            post = self.post_repository.find_one({"_id": ObjectId(req_object.post_id)})
        else:
            post = self.post_repository.find_one(
                {"_id": ObjectId(req_object.post_id), "author": ObjectId(req_object.author_id)})

        if not post:
            return response_object.ResponseFailure.build_not_found_error(message="Post does not exist.")

        try:
            self.post_repository.delete(id=post.id)
            return {"success": True}
        except Exception:
            return response_object.ResponseFailure.build_system_error("Something went error.")
