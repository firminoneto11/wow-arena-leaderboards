from .base import BaseSchema


class WowClassAndSpecAPISchema(BaseSchema):
    blizzard_id: int
    name: str
    icon_url: str


class PvpDataAPISchema(BaseSchema):
    blizzard_id: int
    name: str
    global_rank: int
    cr: int
    played: int
    wins: int
    losses: int
    faction_name: str
    realm: str
    bracket: str
    session: int
    avatar_icon: str | None = None
    wow_class: WowClassAndSpecAPISchema | None = None
    wow_spec: WowClassAndSpecAPISchema | None = None
