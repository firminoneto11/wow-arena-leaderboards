from tortoise import fields

from shared.models import BaseModel


class Sessions(BaseModel):
    class Meta:
        table = "sessions"
        ordering = ["-session"]

    session: int = fields.IntField()


class WowClasses(BaseModel):
    class Meta:
        table = "wow_classes"
        ordering = ["-blizzard_id"]

    blizzard_id: int = fields.BigIntField()
    name: str = fields.CharField(max_length=100)
    icon_url: str | None = fields.TextField(null=True, default=None)


class WowSpecs(BaseModel):
    class Meta:
        table = "wow_specs"
        ordering = ["-blizzard_id"]

    blizzard_id: int = fields.BigIntField()
    name: str = fields.CharField(max_length=100)
    icon_url: str | None = fields.TextField(null=True, default=None)


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
        model_name="core.Sessions", related_name="ladder_data", on_delete=fields.CASCADE
    )

    # Optional Fields
    avatar_icon: str | None = fields.TextField(null=True, default=None)

    # Fks - Optionals
    wow_class: WowClasses | None = fields.ForeignKeyField(
        model_name="core.WowClasses",
        null=True,
        default=None,
        on_delete=fields.SET_NULL,
        related_name="ladder_data",
    )

    wow_spec: WowSpecs | None = fields.ForeignKeyField(
        model_name="core.WowSpecs",
        null=True,
        default=None,
        on_delete=fields.SET_NULL,
        related_name="ladder_data",
    )
