import orm as models
from connection_layer import objects


class Brackets(models.Model):
    tablename = "brackets"
    registry = objects
    fields = {
        "id": models.Integer(primary_key=True, index=True),
        "type": models.String(max_length=20, unique=True)
    }
