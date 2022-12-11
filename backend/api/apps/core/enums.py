from enum import StrEnum


class BracketsEnum(StrEnum):
    TWOS = "2v2"
    THREES = "3v3"
    RBG = "rbg"

    @property
    @classmethod
    def vals(cls) -> list[str]:
        return [cls[el].value for el in cls._member_names_]
