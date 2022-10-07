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
    class_id: int | None
    spec_id: int | None
    avatar_icon: str | None

    @classmethod
    def props_n_types(cls) -> list[tuple[str, str]]:
        props = cls.schema()["properties"]
        return [(prop, props[prop]["type"]) for prop in props]

    @classmethod
    def props(cls) -> list[str]:
        props = cls.schema()["properties"]
        return [prop for prop in props]
