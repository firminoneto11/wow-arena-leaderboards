import orm as models
from connection_layer import objects


class Sessions(models.Model):
    tablename = "sessions"
    registry = objects
    fields = {
        "id": models.Integer(primary_key=True, index=True),
        "session": models.Integer(unique=True),
    }
