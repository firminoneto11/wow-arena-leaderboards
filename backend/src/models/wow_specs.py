import orm as models
from connection_layer import objects
from .wow_classes import WowClasses


class WowSpecs(models.Model):
    tablename = "wow_specs"
    registry = objects
    fields = {
        "id": models.Integer(primary_key=True, index=True),
        "blizz_id": models.Integer(),
        "spec_name": models.String(max_length=50),
        "spec_icon": models.Text(),
        "class_id": models.ForeignKey(WowClasses, on_delete=models.CASCADE)
    }
