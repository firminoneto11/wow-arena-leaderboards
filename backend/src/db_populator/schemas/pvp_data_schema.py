from .base_schema import BaseSchema


class PvpDataSchema(BaseSchema):
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
    wow_class: int | None = None
    wow_spec: int | None = None
