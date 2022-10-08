from enum import Enum

import orm as models

from .base import get_default_fields
from database import engine


class BracketsEnum(Enum):
    _2s = "2s"
    _3s = "3s"
    rbg = "rbg"


class Brackets(models.Model):
    tablename = "brackets"
    registry = engine
    fields = {
        **get_default_fields(),
        # Required Fields
        "name": models.Enum(enum=BracketsEnum, unique=True),
    }
