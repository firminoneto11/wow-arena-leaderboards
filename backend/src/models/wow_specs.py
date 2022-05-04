import orm as models
from connection_layer import objects


class WowSpecs(models.Model):
    tablename = "wow_specs"
    registry = objects
    fields = {
        "id": models.Integer(primary_key=True, index=True),
        "blizz_id": models.Integer(),
        "spec_name": models.String(max_length=50),
        "spec_icon": models.Text()
    }


async def create_wow_spec(**kwargs):
    blizz_id = kwargs.get("blizz_id")
    await WowSpecs.objects.update_or_create(blizz_id=blizz_id, defaults=kwargs)
