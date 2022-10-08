import orm as models

from .base import get_default_fields
from database import engine


class WowSpecs(models.Model):
    tablename = "wow_specs"
    registry = engine
    fields = {
        **get_default_fields(),
        # Required Fields
        "blizzard_id": models.BigInteger(),
        "name": models.String(max_length=50),
        "icon_url": models.Text(),
    }
