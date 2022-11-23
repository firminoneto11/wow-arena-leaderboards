from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def props_n_types(cls) -> list[tuple[str, str]]:
        props = cls.schema()["properties"]
        return [(prop, props[prop]["type"]) for prop in props]

    @classmethod
    def props(cls) -> list[str]:
        props = cls.schema()["properties"]
        return [prop for prop in props]
