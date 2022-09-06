from pydantic import BaseModel
from typing import List, Union
from .player_schema import PlayerSchema


class WowDataSchema(BaseModel):
    bracket_id: int
    bracket_type: str
    total: int
    data: Union[List[PlayerSchema], List]
