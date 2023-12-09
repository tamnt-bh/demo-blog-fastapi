from typing import Union, Optional, List, Dict, Any

from bson import ObjectId
from mongoengine import QuerySet, DoesNotExist

from app.domain.user.entity import UserInCreate, UserInUpdate
from app.infra.database.models.user import UserModel


class UserRepository:
    def __init__(self):
        pass

    def create(self, user: UserInCreate) -> UserModel:
        new_user = UserModel(**user.model_dump())
        new_user.save()
        return new_user

    def get_by_id(self, user_id: Union[str, ObjectId]) -> Optional[UserModel]:
        qs: QuerySet = UserModel.objects(id=user_id)

        try:
            user: UserModel = qs.get()
            return user
        except DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[UserModel]:
        qs: QuerySet = UserModel.objects(email=email)
        try:
            user: UserModel = qs.get()
            return user
        except DoesNotExist:
            return None

    def list(self,
             page_index: int = 1,
             page_size: int = 20
             ) -> List[UserModel]:
        try:
            docs = (UserModel
                    .objects()
                    .order_by("-_id")
                    .skip((page_index - 1) * page_size)
                    .limit(page_size))
            return docs
        except Exception:
            return []

    def count(self, conditions: Dict[str, Union[str, bool, ObjectId]] = {}) -> int:
        try:
            return UserModel._get_collection().count_documents(conditions)
        except Exception:
            return 0

    def delete(self, id: ObjectId) -> bool:
        try:
            UserModel.objects(id=id).delete()
            return True
        except Exception:
            return False

    def update(self, id: ObjectId, data: Union[UserInUpdate, Dict[str, Any]]) -> bool:
        try:
            data = data.model_dump(exclude_none=True) if isinstance(data, UserInUpdate) else data
            UserModel.objects(id=id).update_one(**data, upsert=False)
            return True
        except Exception:
            return False
