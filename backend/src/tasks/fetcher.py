from .fetch_api_token import FetchApiToken
from .fetch_wow_classes import FetchWowClasses
from .fetch_wow_specs import FetchWowSpecs
from .fetch_pvp_data import FetchPvpData
from asyncio import gather, sleep
from models.wow_classes import create_wow_class
from models.wow_specs import create_wow_spec


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

        classes_tasks = []
        for wow_class in wow_classes:
            classes_tasks.append(
                create_wow_class(**wow_class.to_dict())
            )

        specs_tasks = []
        for wow_spec in wow_specs:
            specs_tasks.append(
                create_wow_spec(**wow_spec.to_dict())
            )

        await gather(*classes_tasks, *specs_tasks)

        # Esperando 2 segundos pra não tomar throtlle da api da blizz
        # await sleep(2)
