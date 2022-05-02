from .fetch_api_token import FetchApiToken
from .fetch_wow_classes import FetchWowClasses
from .fetch_wow_specs import FetchWowSpecs
from .fetch_pvp_data import FetchPvpData
from asyncio import gather, sleep


async def fetcher():

    fetch_api_token = FetchApiToken()
    fetch_wow_class = FetchWowClasses()
    fetch_wow_specs = FetchWowSpecs()
    fetch_pvp_data = FetchPvpData()

    # Pegando um access token
    response = await fetch_api_token.run()

    # Checando se não houve erro na primeira etapa (Autenticação)
    if not response["error"]:
        access_token = response["token_stuff"]["access_token"]
        wow_classes, wow_specs = await gather(
            fetch_wow_class.run(access_token=access_token),
            fetch_wow_specs.run(access_token=access_token)
        )

        # Esperando 2 segundos pra não tomar throtlle da api da blizz
        await sleep(2)

        for klass in wow_classes:
            print(klass)

        print("-" * 10)

        for spec in wow_specs:
            print(spec)
