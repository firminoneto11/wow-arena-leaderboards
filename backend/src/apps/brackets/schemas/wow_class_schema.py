from pydantic import BaseModel


class WowClassSchema(BaseModel):
    id: int
    blizz_id: int
    class_name: str
    class_icon: str
