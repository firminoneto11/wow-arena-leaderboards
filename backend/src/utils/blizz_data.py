from settings import LEADERBOARDS_URL, REINOS_BR
from httpx import AsyncClient


async def get_data(session: int, bracket: str, access_token: str):

    # Remontando o endpoint para ser dinâmico
    endpoint = LEADERBOARDS_URL.replace("${session}", str(session))
    endpoint = endpoint.replace("${bracket}", bracket)
    endpoint = endpoint.replace("${accessToken}", access_token)

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
