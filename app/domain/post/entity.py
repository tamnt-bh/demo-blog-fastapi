from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict

from app.domain.shared.entity import BaseEntity, IDModelMixin, PayloadWithFile, Pagination
from app.domain.shared.enum import ExtendedEnum
from app.domain.user.entity import User
from app.domain.user.field import PydanticUserModelType


class PostBase(BaseEntity):
    title: str
    description: str


class PostBaseThumbnail(PostBase):
    thumbnail: Optional[str] = None


class PostInDB(IDModelMixin, PostBaseThumbnail):
    model_config = ConfigDict(from_attributes=True)
    slug: str
    author: PydanticUserModelType
    created_at: datetime
    updated_at: List[datetime]


class PostInCreate(PostBaseThumbnail):
    author: PydanticUserModelType


class PostInCreatePayload(PostBase, PayloadWithFile):
    pass


class Post(PostBaseThumbnail):
    id: str
    author: User
    created_at: datetime
    updated_at: List[datetime]
    slug: str


class PostInUpdate(BaseEntity):
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    updated_at: Optional[List[datetime]] = None


class ManyPostResponse(BaseEntity):
    pagination: Optional[Pagination] = None
    data: Optional[List[Post]] = None

class SearchByPost(str, ExtendedEnum):
    TITLE = "title"
    AUTHOR = "author"
