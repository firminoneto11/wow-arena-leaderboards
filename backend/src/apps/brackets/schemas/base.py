from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Meta:
        arbitrary_types_allowed = True
