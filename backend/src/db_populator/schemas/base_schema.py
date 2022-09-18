from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        arbitrary_types_allowed = True
