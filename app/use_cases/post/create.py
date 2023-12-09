from fastapi import Depends

from app.domain.post.entity import PostInCreate, Post, PostInDB
from app.domain.user.entity import UserInDB, User
from app.infra.database.models.post import PostModel
from app.infra.post.post_repository import PostRepository
from app.shared import request_object, use_case, response_object


class CreatePostRequestObject(request_object.ValidRequestObject):
    def __init__(self, obj_in: PostInCreate):
        self.obj_in = obj_in

    @classmethod
    def builder(cls, payload: PostInCreate) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if payload is None:
            invalid_req.add_error("payload", "Invalid payload")

        if invalid_req.has_errors():
            return invalid_req

        return CreatePostRequestObject(obj_in=payload)


class CreatePostUseCase(use_case.UseCase):
    def __init__(self, post_repository: PostRepository = Depends(PostRepository)):
        self.post_repository = post_repository

    def process_request(self, req_object: CreatePostRequestObject):
        post_in = req_object.obj_in

        try:
            post: PostModel = self.post_repository.create(obj_in=post_in)
            return Post(**PostInDB.model_validate(post).model_dump(exclude=({"author"})),
                        author=User(**UserInDB.model_validate(post.author).model_dump()))
        except Exception:
            return response_object.ResponseFailure.build_system_error("Something went error.")
