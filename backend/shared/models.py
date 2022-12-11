from datetime import datetime

from tortoise.models import Model
from tortoise import fields


class BaseModel(Model):
    class Meta:
        abstract = True

    # Auto Added field
    id: int

    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)
