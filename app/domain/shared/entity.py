import json
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.domain.shared.field import PydanticObjectId


class BaseEntity(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    @classmethod
    def from_mongo(cls, data: dict, id_str=False):
        if not data:
            return data
        id = data.pop("_id", None) if not id_str else str(data.pop("_id", None))
        return cls(**dict(data, id=id))

    def to_mongo(self, **kwargs):
        exclude_unset = kwargs.pop("exclude_unset", True)
        by_alias = kwargs.pop("by_alias", True)

        parsed = self.dict(
            exclude_unset=exclude_unset,
            by_alias=by_alias,
            **kwargs,
        )

        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = parsed.pop("id")

        return parsed


class Pagination(BaseModel):
    total: Optional[int] = 0
    page_index: Optional[int] = 1
    total_pages: Optional[int] = None


class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("created_at", "updated_at", mode="after")
    def set_datetime_now(cls, value: datetime) -> datetime:
        return value or datetime.utcnow()


class IDModelMixin(BaseModel):
    id: Optional[PydanticObjectId] = None


class PayloadWithFile:
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
