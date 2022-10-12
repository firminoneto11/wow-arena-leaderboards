import orm as models

from ..base import get_default_fields
from database import engine


class Brackets(models.Model):
    tablename = "brackets"
    registry = engine
    fields = {
        **get_default_fields(),
        # Required Fields
        "name": models.String(max_length=10, unique=True),
    }
