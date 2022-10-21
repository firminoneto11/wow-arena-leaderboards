import ormar as models

from .base import BaseModel


class WowSpecs(BaseModel):
    class Meta:
        tablename = "wow_specs"

    blizzard_id: int = models.BigInteger()
    name: str = models.String(max_length=50)
    icon_url: str = models.Text()

    def dict(self) -> dict:
        return super().dict(include={"blizzard_id", "name", "icon_url"})
