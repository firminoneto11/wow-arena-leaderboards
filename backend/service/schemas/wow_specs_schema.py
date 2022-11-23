from .base_schema import BaseSchema


class WowSpecsSchema(BaseSchema):
    blizzard_id: int
    name: str
    icon_url: str | None
