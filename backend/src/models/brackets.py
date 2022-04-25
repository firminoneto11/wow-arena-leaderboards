import orm as models
from connection_layer import objects
from enum import Enum


class BracketsEnum(Enum):
    twos = "2v2"
    thres = "3v3"
    rbg = "rbg"


class Brackets(models.Model):
    tablename = "brackets"
    registry = objects
    fields = {
        "id": models.Integer(primary_key=True, index=True),
        "type": models.Enum(BracketsEnum, unique=True),
    }
