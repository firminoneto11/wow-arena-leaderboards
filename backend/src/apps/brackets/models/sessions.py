import orm as models

from .base import get_default_fields
from database import engine


class Sessions(models.Model):
    tablename = "sessions"
    registry = engine
    fields = {
        **get_default_fields(),
        # Required Fields
        "session": models.Integer(unique=True),
    }

    # Types
    session: int
