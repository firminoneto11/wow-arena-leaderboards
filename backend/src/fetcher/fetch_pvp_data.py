from asyncio import gather
from httpx import AsyncClient
from asyncio import gather
from typing import List, Dict
from utils import PvpDataDataclass
from settings import (
    TIMEOUT, REINOS_BR, PVP_RATING_API
)


class FetchPvpData:

    access_token: str

    def refactor_endpoint(self, session: int, bracket: str):
        return PVP_RATING_API.replace("${session}", str(session)).replace("${bracket}", bracket).replace(
            "${accessToken}", self.access_token
        )

    async def run(self, access_token: str):
        self.access_token = access_token
        return await self.get_data()

    async def get_data(self) -> Dict[str, List[PvpDataDataclass]]:

        # TODO: Passar o 'session' e a 'bracket' como parâmetro
        data = await gather(
            self.get_brazilian_data(session=32, bracket="2v2"),
            self.get_brazilian_data(session=32, bracket="3v3"),
            self.get_brazilian_data(session=32, bracket="rbg"),
        )

        data = {
            "twos": self.clean_data(data[0]),
            "thres": self.clean_data(data[1]),
            "rbg": self.clean_data(data[2]),
        }

        return data

    async def get_brazilian_data(self, session: int, bracket: str):

        # Remontando o endpoint para ser dinâmico
        endpoint = self.refactor_endpoint(session=session, bracket=bracket)

        async with AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(endpoint)
            data = response.json()
            if response.status_code == 200:
                brazilian_players = list(filter(
                    lambda player: player["character"]["realm"]["slug"] in REINOS_BR,
                    data["entries"]
                ))
                return brazilian_players
            else:
                raise Exception(f"Houve um problema no status code ao solicitar os dados para a bracket '{bracket}'")

    def clean_data(self, raw_data: List[dict]):
        cleaned_data = []
        for el in raw_data:
            cleaned_data.append(
                PvpDataDataclass(

                    blizz_id=el["character"]["id"],

                    name=el["character"]["name"],

                    global_rank=el["rank"],

                    cr=el["rating"],

                    played=el["season_match_statistics"]["played"],

                    wins=el["season_match_statistics"]["won"],

                    losses=el["season_match_statistics"]["lost"],

                    faction_name=el["faction"]["type"],

                    realm=el["character"]["realm"]["slug"],

                    class_id=None,

                    spec_id=None,

                    avatar_icon=None,

                )
            )
        return cleaned_data
