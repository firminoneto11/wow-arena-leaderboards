from dataclasses import dataclass
from typing import List


@dataclass
class PlayerData:
    name: str  # 'character.name'
    global_rank: int  # 'rank'
    cr: int  # 'rating'
    faction_name: str  # 'faction.type'
    realm: str  # 'character.realm.slug'
    played: int  # 'season_match_statistics.played'
    wins: int  # 'season_match_statistics.won'
    losses: int  # 'season_match_statistics.lost'
    player_id_blizz_db: int  # 'character.id'


@dataclass
class DadosBracket:
    bracket: str
    dados: List[PlayerData]


@dataclass
class WowClassesDataclass:
    blizz_id: int = 0
    class_name: str = ""
    class_icon: str = ""
