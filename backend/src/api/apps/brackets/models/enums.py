from enum import Enum


class BracketsEnum(Enum):
    _2s = "2v2"
    _3s = "3v3"
    rbg = "rbg"

    @classmethod
    def list_values(cls) -> list[str]:
        return [cls[el].value for el in cls._member_names_]
