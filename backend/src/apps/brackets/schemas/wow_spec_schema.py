from pydantic import BaseModel


class WowSpecSchema(BaseModel):
    id: int
    blizz_id: int
    spec_name: str
    spec_icon: str
