from .fetch_api_token import FetchApiToken
from .fetch_wow_classes import FetchWowClasses
from .fetch_wow_specs import FetchWowSpecs
from .fetch_pvp_data import FetchPvpData
from asyncio import gather, sleep
from models.wow_classes import create_wow_class
from models.wow_specs import create_wow_spec
from typing import List
from utils import WowClassesDataclass, WowSpecsDataclass


async def to_db(wow_classes: List[WowClassesDataclass] = [], wow_specs: List[WowSpecsDataclass] = []):
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

    pvp_data_tasks = []
    # for pd in pvp_data:
    #     pass

    await gather(*classes_tasks, *specs_tasks)


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

        pvp_data = await(
            fetch_pvp_data.run(access_token=access_token)
        )

        # Esperando 2 segundos pra não tomar throtlle da api da blizz
        await sleep(2)

        # TODO: Iterar em cada elemento do pvp_data e fazer um fetch no PROFILE_API para pegar a spec id e class id

        await to_db(wow_classes=wow_classes, wow_specs=wow_specs)
