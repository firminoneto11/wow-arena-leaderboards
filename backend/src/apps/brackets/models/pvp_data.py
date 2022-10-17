import orm as models

from .base import get_default_fields
from .sessions import Sessions
from .wow_classes import WowClasses
from .wow_specs import WowSpecs
from database import engine


class PvpData(models.Model):
    tablename = "pvp_data"
    registry = engine
    fields = {
        **get_default_fields(),
        # Required Fields
        "blizzard_id": models.BigInteger(),
        "name": models.String(max_length=50),
        "global_rank": models.Integer(),
        "cr": models.Integer(),
        "played": models.Integer(),
        "wins": models.Integer(),
        "losses": models.Integer(),
        "faction_name": models.String(max_length=50),
        "realm": models.String(max_length=50),
        "bracket": models.String(max_length=10),
        # FK's - Required
        "session": models.ForeignKey(to=Sessions, on_delete=models.CASCADE),
        # Optional Fields
        "avatar_icon": models.Text(allow_null=True),
        # Fk's - Optionals
        "wow_class": models.ForeignKey(to=WowClasses, allow_null=True, on_delete=models.SET_NULL),
        "wow_spec": models.ForeignKey(to=WowSpecs, allow_null=True, on_delete=models.SET_NULL),
    }
