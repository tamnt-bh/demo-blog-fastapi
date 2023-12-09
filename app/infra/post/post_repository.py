from typing import List, Dict, Union, Optional, Any

from bson import ObjectId
from mongoengine import QuerySet, DoesNotExist

from app.domain.post.entity import PostInCreate, PostInUpdate
from app.infra.database.models.post import PostModel


class PostRepository:
    def __init__(self):
        pass

    def create(self, obj_in: PostInCreate) -> PostModel:
        new_post = PostModel(**obj_in.model_dump())
        new_post.save()
        return new_post

    def get_by_id(self, post_id: Union[str, ObjectId]) -> Optional[PostModel]:
        qs: QuerySet = PostModel.objects(id=post_id)

        try:
            post: PostModel = qs.get()
            return post
        except DoesNotExist:
            return None

    def list(self,
             page_index: int = 1,
             page_size: int = 20
             ) -> List[PostModel]:
        try:
            docs = (PostModel
                    .objects()
                    .order_by("-_id")
                    .skip((page_index - 1) * page_size)
                    .limit(page_size))
            return docs
        except Exception:
            return []

    def count(self, conditions: Dict[str, Union[str, bool, ObjectId]] = {}) -> int:
        try:
            return PostModel._get_collection().count_documents(conditions)
        except Exception:
            return 0

    def find(self, skip: int, limit: int, conditions: Dict[str, Union[str, bool, ObjectId]] = {}) -> List[PostModel]:
        try:
            docs = PostModel._get_collection().find(conditions).skip(skip).limit(limit)
            return [PostModel.from_mongo(doc) for doc in docs] if docs else []
        except Exception:
            return []

    def find_one(self, conditions: Dict[str, Union[str, bool, ObjectId]] = {}) -> PostModel:
        try:
            doc = PostModel._get_collection().find_one(conditions)
            return PostModel.from_mongo(doc) if doc else None
        except Exception as e:
            print(e)
            return None

    def update(self, id: ObjectId, data: Union[PostInUpdate, Dict[str, Any]]) -> bool:
        try:
            data = data.model_dump(exclude_none=True) if isinstance(data, PostInUpdate) else data
            PostModel.objects(id=id).update_one(**data, upsert=False)
            return True
        except Exception:
            return False

    def delete(self, id: ObjectId) -> bool:
        try:
            PostModel.objects(id=id).delete()
            return True
        except Exception:
            return False
