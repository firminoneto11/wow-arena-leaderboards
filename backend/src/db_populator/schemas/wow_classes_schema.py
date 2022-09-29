from .base_schema import BaseSchema


class WowClassSchema(BaseSchema):
    blizzard_id: int
    name: str
    icon_url: str = ""
