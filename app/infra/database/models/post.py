from datetime import datetime
from random import sample

from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField
from slugify import slugify


class PostModel(Document):
    title = StringField(required=True)
    slug = StringField(required=True, unique=True)
    description = StringField(required=True)
    thumbnail = StringField(required=False)
    created_at = DateTimeField(required=True)
    updated_at = ListField(DateTimeField(), required=False)
    author = ReferenceField("UserModel", required=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
            random_numbers = "".join(str(x) for x in sample(range(10), 5))
            self.slug = slugify(self.title) + "-" + random_numbers
        if not self.updated_at:
            self.updated_at = [datetime.utcnow()]
        else:
            self.updated_at.append(datetime.utcnow())
        return super(PostModel, self).save(*args, **kwargs)

    @classmethod
    def from_mongo(cls, data: dict, id_str=False):
        if not data:
            return data
        id = data.pop("_id", None) if not id_str else str(data.pop("_id", None))
        if "_cls" in data:
            data.pop("_cls", None)
        return cls(**dict(data, id=id))

    meta = {
        "collection": "Posts",
        "indexes": ["title", "slug", "author"],
        "allow_inheritance": True,
        "index_cls": False,
    }
