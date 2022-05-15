from dataclasses import dataclass


@dataclass
class PvpDataDataclass:
    blizz_id: int
    name: str
    class_id: int
    spec_id: int
    global_rank: int
    cr: int
    played: int
    wins: int
    losses: int
    faction_name: str
    realm: str
    avatar_icon: str

    def to_dict(self) -> dict:
        return self.__dict__


@dataclass
class WowClassesDataclass:
    blizz_id: int = 0
    class_name: str = ""
    class_icon: str = ""

    def to_dict(self) -> dict:
        return self.__dict__


@dataclass
class WowSpecsDataclass:
    blizz_id: int = 0
    spec_name: str = ""
    spec_icon: str = ""

    def to_dict(self) -> dict:
        return self.__dict__


# TIP: Sempre que realizar alguma alteração no dataclass, replique a alteração no schema correspondente!
