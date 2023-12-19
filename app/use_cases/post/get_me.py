import math
from typing import List

from bson import ObjectId
from fastapi import Depends

from app.domain.post.entity import Post, PostInDB, ManyPostResponse
from app.domain.shared.entity import Pagination
from app.domain.user.entity import User, UserInDB
from app.infra.database.models.post import PostModel
from app.infra.post.post_repository import PostRepository
from app.shared import request_object, use_case


class GetPostMeObjectRequest(request_object.ValidRequestObject):
    def __init__(self, author_id: ObjectId, page_index, page_size):
        self.author_id = author_id
        self.page_index = page_index
        self.page_size = page_size

    @classmethod
    def builder(cls, author_id: ObjectId, page_index: int, page_size: int) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if not isinstance(author_id, ObjectId):
            invalid_req.add_error("author_id", "Invalid ID")

        if invalid_req.has_errors():
            return invalid_req
        return GetPostMeObjectRequest(author_id=author_id, page_index=page_index, page_size=page_size)


class GetPostMeUseCase(use_case.UseCase):
    def __init__(self, post_repository: PostRepository = Depends(PostRepository)):
        self.post_repository = post_repository

    def process_request(self, req_object: GetPostMeObjectRequest):
        posts: List[PostModel] = self.post_repository.find(conditions={"author": req_object.author_id},
                                                           skip=(req_object.page_index - 1) * req_object.page_size,
                                                           limit=req_object.page_size,
                                                           )
        total = self.post_repository.count({"author": req_object.author_id})

        return ManyPostResponse(pagination=Pagination(total=total,
                                                      page_index=req_object.page_index,
                                                      total_pages=math.ceil(total / req_object.page_size)),
                                data=[Post(**PostInDB.model_validate(post).model_dump(exclude=({"author"})),
                                           author=User(**UserInDB.model_validate(post.author).model_dump())) for post in
                                      posts])
