import ormar as models

from .base import BaseModel


class Sessions(BaseModel):
    class Meta:
        tablename = "sessions"

    session: int = models.Integer(unique=True)
