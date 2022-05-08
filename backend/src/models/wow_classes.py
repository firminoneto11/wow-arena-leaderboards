import orm as models
from connection_layer import objects
from datetime import datetime


class WowClasses(models.Model):
    tablename = "wow_classes"
    registry = objects
    fields = {
        "id": models.Integer(primary_key=True, index=True),
        "blizz_id": models.Integer(),
        "class_name": models.String(max_length=50),
        "class_icon": models.Text(),
        "updated_at": models.DateTime(default=lambda: datetime.now())
    }


async def create_wow_class(**kwargs):
    blizz_id = kwargs.get("blizz_id")
    await WowClasses.objects.update_or_create(blizz_id=blizz_id, defaults=kwargs)
