from tortoise import fields

from shared.models import BaseModel
from .wow_classes import WowClasses
from .wow_specs import WowSpecs
from .sessions import Sessions


class PvpData(BaseModel):
    class Meta:
        table = "pvp_data"
        ordering = ["-cr"]

    # Required Fields
    blizzard_id: int = fields.BigIntField()
    name: str = fields.CharField(max_length=100)
    global_rank: int = fields.IntField()
    cr: int = fields.IntField()
    played: int = fields.IntField()
    wins: int = fields.IntField()
    losses: int = fields.IntField()
    faction_name: str = fields.CharField(max_length=100)
    realm: str = fields.CharField(max_length=100)
    bracket: str = fields.CharField(max_length=10)

    # FKs - Required
    session: Sessions = fields.ForeignKeyField(
        model_name="api.apps.core.models.Sessions", related_name="ladder_data", on_delete=fields.CASCADE
    )

    # Optional Fields
    avatar_icon: str | None = fields.TextField(null=True, default=None)

    # Fks - Optionals
    wow_class: WowClasses | None = fields.ForeignKeyField(
        model_name="api.apps.core.models.WowClasses",
        nullable=True,
        default=None,
        on_delete=fields.SET_NULL,
        related_name="ladder_data",
    )
    wow_spec: WowSpecs | None = fields.ForeignKeyField(
        model_name="api.apps.core.models.WowSpecs",
        nullable=True,
        default=None,
        on_delete=fields.SET_NULL,
        related_name="ladder_data",
    )
