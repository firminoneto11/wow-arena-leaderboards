import orm as models
from connection_layer import objects
from datetime import datetime
from .brackets import Brackets


class PvpData(models.Model):
    tablename = "pvp_data"
    registry = objects
    fields = {
        "id": models.Integer(primary_key=True, index=True),
        "blizz_id": models.Integer(),
        "name": models.String(max_length=100),
        "class_id": models.Integer(allow_null=True),
        "spec_id": models.Integer(allow_null=True),
        "global_rank": models.Integer(),
        "cr": models.Integer(),
        "played": models.Integer(),
        "wins": models.Integer(),
        "losses": models.Integer(),
        "faction_name": models.String(max_length=50),
        "realm": models.String(max_length=50),
        "avatar_icon": models.Text(allow_null=True),
        "bracket_id": models.ForeignKey(to=Brackets, on_delete=models.CASCADE),
        "updated_at": models.DateTime(default=lambda: datetime.now())
    }


async def create_pvp_data(**kwargs):
    blizz_id = kwargs.get("blizz_id")
    await PvpData.objects.update_or_create(blizz_id=blizz_id, defaults=kwargs)
