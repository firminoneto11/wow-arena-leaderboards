from pydantic import BaseModel
from .wow_class_schema import WowClassSchema
from .wow_spec_schema import WowSpecSchema
from typing import Union


class PlayerSchema(BaseModel):
    id: int
    blizz_id: int
    name: str
    global_rank: int
    cr: int
    played: int
    wins: int
    losses: int
    faction_name: str
    realm: str
    avatar_icon: Union[str, None]

    wow_class: Union[WowClassSchema, None]
    wow_spec: Union[WowSpecSchema, None]
