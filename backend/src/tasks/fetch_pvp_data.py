from asyncio import gather
from httpx import AsyncClient
from settings import PVP_RATING_API, REINOS_BR
from asyncio import gather
from utils import PvpDataDataclass
from typing import List, Dict
from settings import TIMEOUT


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

    """
    async def write_to_json_file(self, data: List[DadosBracket]):
        async def gerar_dump(dt: List[PvpDataDataclass]):
            print("Gerando dump dos dados")
            return json.dumps(list(map(
                lambda el: el.__dict__,
                dt
            )))
        async def escrever_no_arquivo(dt, tipo: str):
            nome = None
            if tipo == '2v2':
                nome = '../twos_data.json'
            elif tipo == '3v3':
                nome = '../thres_data.json'
            else:
                nome = '../rbg_data.json'
            print(f"Escrevendo no arquivo '{nome}'")
            with open(file=nome, mode='w', encoding='utf-8') as f:
                f.write(dt)

        twos = data[0]
        thres = data[1]
        rbg = data[2]

        dados = await gather(
            gerar_dump(dt=twos.dados),
            gerar_dump(dt=thres.dados),
            gerar_dump(dt=rbg.dados),
        )

        await gather(
            escrever_no_arquivo(dt=dados[0], tipo=twos.bracket),
            escrever_no_arquivo(dt=dados[1], tipo=thres.bracket),
            escrever_no_arquivo(dt=dados[2], tipo=rbg.bracket),
        )
    """
