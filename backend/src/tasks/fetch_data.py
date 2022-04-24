from asyncio import gather
from httpx import AsyncClient
from decouple import config
from settings import BLIZZARD_TOKENS_URL, LEADERBOARDS_URL, REINOS_BR
import json
from asyncio import gather


# Formato do retorno da api da Blizzard
token_stuff_format = {
    "access_token": str,
    "token_type": str,
    "expires_in": int,
    "sub": str,
}


class RetriveBlizzardData:

    @classmethod
    def refactor_endpoint(cls, session: int, bracket: str, access_token: str):
        return LEADERBOARDS_URL.replace("${session}", str(session)).replace("${bracket}", bracket).replace(
            "${accessToken}", access_token
        )

    @classmethod
    async def write_to_json_file(cls, data):

        async def gerar_dump(dt):
            print('Gerando dump de string')
            return json.dumps(dt)

        async def escrever_no_arquivo(dt, tipo: str):
            print('Escrevendo arquivo')

            nome = None

            if tipo == '2v2':
                nome = '../twos_data.json'
            elif tipo == '3v3':
                nome = '../thres_data.json'

            with open(file=nome, mode='w', encoding='utf-8') as f:
                f.write(dt)

        dados = await gather(
            gerar_dump(dt=data[0]), gerar_dump(dt=data[1])
        )

        await gather(
            escrever_no_arquivo(dt=dados[0], tipo='2v2'), escrever_no_arquivo(dt=dados[1], tipo='3v3')
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
    async def get_data(cls, session: int, bracket: str, access_token: str):

        # Remontando o endpoint para ser dinâmico
        endpoint = cls.refactor_endpoint(session=session, bracket=bracket, access_token=access_token)

        async with AsyncClient() as client:
            response = await client.get(endpoint)

            data = response.json()

            if response.status_code == 200:
                jogadores_brasileiros = list(filter(
                    lambda player: player["character"]["realm"]["slug"] in REINOS_BR,
                    data["entries"]
                ))
                return jogadores_brasileiros
            else:
                print(response)
                print(data)
                raise Exception(f"Houve um problema no status code ao solicitar os dados para a bracket '{bracket}'")

    @classmethod
    async def mount_data(cls):
        """ Este método """

        token_stuff: dict = await cls.get_token_stuff()

        for key, val in token_stuff.items():
            print(key, val)

        if token_stuff is not None:

            access_token = token_stuff.get("access_token")

            requests = [
                cls.get_data(session=32, bracket="2v2", access_token=access_token),
                cls.get_data(session=32, bracket="3v3", access_token=access_token),
                # cls.get_data(session=32, bracket="10v10", access_token=access_token),
            ]

            data = await gather(*requests)

            await cls.write_to_json_file(data)

        else:
            # Fazer algo quando não tiver access tokens
            pass


# TODO: Ver como é a bracket de RBG
