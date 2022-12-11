from tortoise import fields

from shared.models import BaseModel


class Sessions(BaseModel):
    class Meta:
        table = "sessions"
        ordering = ["-session"]

    session: int = fields.IntField()
