import ormar as models

from .base import BaseModel


class Sessions(BaseModel):
    class Meta:
        tablename = "sessions"

    session: int = models.Integer(unique=True)

    def dict(self) -> dict:
        return super().dict(include={"session"})
