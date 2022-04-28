from .fetch_api_token import FetchApiToken
from .fetch_wow_classes import FetchWowClasses
from asyncio import sleep


async def fetcher():

    fetch_api_token = FetchApiToken()
    fetch_wow_class = FetchWowClasses()

    # Pegando um access token
    response = await fetch_api_token.run()

    # Checando se não houve erro na primeira etapa (Autenticação)
    if not response["error"]:
        access_token = response["token_stuff"]["access_token"]
        await fetch_wow_class.run(access_token=access_token)
