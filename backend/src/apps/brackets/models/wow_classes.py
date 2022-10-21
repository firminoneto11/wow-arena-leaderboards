import orm as models

from .base import get_default_fields
from database import engine


class WowClasses(models.Model):
    tablename = "wow_classes"
    registry = engine
    fields = {
        **get_default_fields(),
        # Required Fields
        "blizzard_id": models.BigInteger(),
        "name": models.String(max_length=50),
        "icon_url": models.Text(),
    }

    # Types
    blizzard_id: int
    name: str
    icon_url: str

    @property
    def asDict(self) -> dict:
        return {
            "blizzard_id": self.blizzard_id,
            "name": self.name,
            "icon_url": self.icon_url,
        }
