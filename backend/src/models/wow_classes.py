import orm as models
from connection_layer import objects


class WowClasses(models.Model):
    tablename = "wow_classes"
    registry = objects
    fields = {
        "id": models.Integer(primary_key=True, index=True),
        "blizz_id": models.Integer(),
        "class_name": models.String(max_length=50),
        "class_icon": models.Text()
    }
