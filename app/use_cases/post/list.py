import math
from typing import Optional, List, Dict, Any

from bson import ObjectId
from fastapi import Depends

from app.domain.post.entity import PostInDB, Post, ManyPostResponse, SearchByPost
from app.domain.shared.entity import Pagination
from app.domain.user.entity import User, UserInDB
from app.infra.database.models.post import PostModel
from app.infra.database.models.user import UserModel
from app.infra.post.post_repository import PostRepository
from app.infra.user.user_repository import UserRepository
from app.shared import request_object, use_case


class ListPostRequestObject(request_object.ValidRequestObject):
    def __init__(self, search: Optional[str], search_by: Optional[str], sort: Optional[Dict[str, int]] = None,
                 page_index: int = 1, page_size: int = 20):
        self.page_index = page_index
        self.page_size = page_size
        self.search = search
        self.search_by = search_by
        self.sort = sort

    @classmethod
    def builder(cls, search: Optional[str], search_by: Optional[str], sort: Optional[Dict[str, int]] = None,
                page_index: int = 1,
                page_size: int = 20):
        return ListPostRequestObject(page_index=page_index, page_size=page_size, search=search, search_by=search_by,
                                     sort=sort)


class ListPostUseCase(use_case.UseCase):
    def __init__(
            self,
            post_repository: PostRepository = Depends(PostRepository),
            user_repository: UserRepository = Depends(UserRepository)
    ):
        self.post_repository = post_repository
        self.user_repository = user_repository

    def process_request(self, req_object: ListPostRequestObject):
        match_pipeline: Optional[Dict[str, Any]] = None

        if isinstance(req_object.search, str):
            if req_object.search_by is SearchByPost.TITLE:
                match_pipeline = {
                    "$match": {
                        "title": {"$regex": req_object.search, "$options": "i"}
                    }
                }
            else:
                authors: Optional[List[UserModel]] = self.user_repository.find(conditions={
                    "fullname": {"$regex": req_object.search, "$options": "i"}
                })
                match_pipeline = {
                    "$match": {
                        "author": {"$in": [ObjectId(author.id) for author in authors]}
                    }
                }

        posts: Optional[List[PostModel]] = self.post_repository.list(page_size=req_object.page_size,
                                                                     page_index=req_object.page_index,
                                                                     sort=req_object.sort,
                                                                     match_pipeline=match_pipeline
                                                                     )

        total = self.post_repository.count_list(match_pipeline=match_pipeline)

        return ManyPostResponse(pagination=Pagination(total=total,
                                                      page_index=req_object.page_index,
                                                      total_pages=math.ceil(total / req_object.page_size)),
                                data=[Post(**PostInDB.model_validate(post).model_dump(exclude=({"author"})),
                                           author=User(**UserInDB.model_validate(post.author).model_dump())) for post in
                                      posts])
