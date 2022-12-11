from tortoise import fields

from shared.models import BaseModel


class WowClasses(BaseModel):
    class Meta:
        table = "wow_classes"
        ordering = ["-blizzard_id"]

    blizzard_id: int = fields.BigIntField()
    name: str = fields.CharField(max_length=100)
    icon_url: str | None = fields.TextField(null=True, default=None)
