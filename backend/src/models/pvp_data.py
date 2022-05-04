import orm as models
from connection_layer import objects


class PvpData(models.Model):
    tablename = "pvp_data"
    registry = objects
    fields = {
        "id": models.Integer(primary_key=True, index=True),
        "blizz_id": models.Integer(),
        "name": models.String(max_length=100),
        "class_id": models.Integer(),
        "spec_id": models.Integer(),
        "global_rank": models.Integer(),
        "cr": models.Integer(),
        "played": models.Integer(),
        "wins": models.Integer(),
        "losses": models.Integer(),
        "faction_name": models.String(max_length=50),
        "realm": models.String(max_length=50),
    }
