from asyncio import gather
from httpx import AsyncClient
from decouple import config
from settings import BLIZZARD_TOKENS_URL, PVP_RATING_API, REINOS_BR
import json
from asyncio import gather
from utils import PlayerData, DadosBracket
from typing import List


# Formato do retorno da api da Blizzard
token_stuff_format = {
    "access_token": str,
    "token_type": str,
    "expires_in": int,
    "sub": str,
}


class RetrievePvpData:

    @classmethod
    def refactor_endpoint(cls, session: int, bracket: str, access_token: str):
        return PVP_RATING_API.replace("${session}", str(session)).replace("${bracket}", bracket).replace(
            "${accessToken}", access_token
        )

    @classmethod
    async def write_to_json_file(cls, data: List[DadosBracket]):

        async def gerar_dump(dt: List[PlayerData]):
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

    @classmethod
    async def get_token_stuff(cls):
        """ Este método faz uma requisição ao servidor da blizzard para pegar um access token atualizado """

        credential_string = config("ENCODED_CREDENTIALS")
        content_type = "application/x-www-form-urlencoded"

        headers = {
            "Authorization": credential_string,
            "Content-Type": content_type
        }

        body = "grant_type=client_credentials"

        async with AsyncClient() as client:

            try:
                response = await client.post(
                    url=BLIZZARD_TOKENS_URL,
                    headers=headers,
                    data=body
                )
            except Exception as error:
                print((
                    f"\nOcorreu um erro ao pegar o access token da blizzard. Não será possível pegar os dados! "
                    f"Mais informações sobre o erro: {error}\n"
                ))
                return

            data = response.json()

            if response.status_code == 200:
                return data
            else:
                print(response)
                print(data)
                raise Exception("Houve um problema no status code ao solicitar o access token")

    @classmethod
    async def get_brazilian_data(cls, session: int, bracket: str, access_token: str):

        # Remontando o endpoint para ser dinâmico
        endpoint = cls.refactor_endpoint(session=session, bracket=bracket, access_token=access_token)

        async with AsyncClient() as client:
            response = await client.get(endpoint)
            data = response.json()
            if response.status_code == 200:
                brazilian_players = list(filter(
                    lambda player: player["character"]["realm"]["slug"] in REINOS_BR,
                    data["entries"]
                ))
                return brazilian_players
            else:
                print(response)
                print(data)
                raise Exception(f"Houve um problema no status code ao solicitar os dados para a bracket '{bracket}'")

    @classmethod
    async def mount_data(cls, raw_data: List[dict]):
        cleaned_data = []

        for el in raw_data:
            cleaned_data.append(
                PlayerData(

                    name=el["character"]["name"],

                    global_rank=el["rank"],

                    cr=el["rating"],

                    faction_name=el["faction"]["type"],

                    realm=el["character"]["realm"]["slug"],

                    played=el["season_match_statistics"]["played"],

                    wins=el["season_match_statistics"]["won"],

                    losses=el["season_match_statistics"]["lost"],

                    player_id_blizz_db=el["character"]["id"],

                )
            )

        return cleaned_data

    @classmethod
    async def get_data(cls, access_token: str):

        data = await gather(
            cls.get_brazilian_data(session=32, bracket="2v2", access_token=access_token),
            cls.get_brazilian_data(session=32, bracket="3v3", access_token=access_token),
            cls.get_brazilian_data(session=32, bracket="rbg", access_token=access_token),
        )

        mounted_data = await gather(
            cls.mount_data(data[0]),
            cls.mount_data(data[1]),
            cls.mount_data(data[2]),
        )

        mounted_data = [
            DadosBracket(bracket='2v2', dados=mounted_data[0]),
            DadosBracket(bracket='3v3', dados=mounted_data[1]),
            DadosBracket(bracket='rbg', dados=mounted_data[2]),
        ]

        await cls.write_to_json_file(data=mounted_data)

        return mounted_data

    @classmethod
    async def run(cls):

        token_stuff: dict = await cls.get_token_stuff()

        for key, val in token_stuff.items():
            print(key, val)

        if token_stuff is not None:
            mounted_data = await cls.get_data(access_token=token_stuff.get("access_token"))
        else:
            raise Exception(
                "Não será possível continuar pois ocorreu um problema ao solicitar o access token para a Blizzard"
            )
