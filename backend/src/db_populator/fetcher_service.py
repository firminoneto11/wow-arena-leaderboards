from logging import Logger

from fetcher import FetchApiToken, FetchWowClasses, FetchWowSpecs, FetchPvpData, FetchWowMedia

from models import Brackets, create_wow_class, create_wow_spec, create_pvp_data

from utils import WowClassesDataclass as WowClassesDt, WowSpecsDataclass as WowSpecsDt, PvpDataDataclass as PvpDataDt

from settings import DELAY, UPDATE_EVERY

from asyncio import gather, sleep, run as run_in_async_mode
from time import time
from typing import List, Dict


async def to_db(wow_classes: List[WowClassesDt], wow_specs: List[WowSpecsDt], pvp_data: Dict[str, List[PvpDataDt]]):
    classes_tasks = []
    for wow_class in wow_classes:
        classes_tasks.append(create_wow_class(**wow_class.to_dict()))

    specs_tasks = []
    for wow_spec in wow_specs:
        specs_tasks.append(create_wow_spec(**wow_spec.to_dict()))

    pvp_data_tasks = []
    for key in pvp_data.keys():
        if key == "twos":
            bracket = await Brackets.objects.get(type="2v2")
            for pd in pvp_data[key]:
                pvp_data_tasks.append(create_pvp_data(pd=pd, bracket=bracket))
        elif key == "thres":
            bracket = await Brackets.objects.get(type="3v3")
            for pd in pvp_data[key]:
                pvp_data_tasks.append(create_pvp_data(pd=pd, bracket=bracket))
        else:
            bracket = await Brackets.objects.get(type="rbg")
            for pd in pvp_data[key]:
                pvp_data_tasks.append(create_pvp_data(pd=pd, bracket=bracket))

    await gather(*classes_tasks, *specs_tasks, *pvp_data_tasks)


async def fetcher(logger: Logger) -> None:

    inicio = time()

    fetch_api_token = FetchApiToken()
    fetch_wow_class = FetchWowClasses()
    fetch_wow_specs = FetchWowSpecs()
    fetch_pvp_data = FetchPvpData()
    fetch_wow_media = FetchWowMedia()

    print("\n1 - Fazendo um fetch no access token...\n")

    # Pegando um access token
    response = await fetch_api_token.run()
    print(response)

    # Checando se não houve erro na primeira etapa (Autenticação)
    if not response["error"]:

        access_token = response["token_stuff"]["access_token"]

        print("\n2 - Fazendo um fetch nos dados de pvp do wow...\n")
        pvp_data = await fetch_pvp_data.run(access_token=access_token)

        print("\n3 - Fazendo um fetch nos dados das classes e specs...\n")
        wow_classes, wow_specs = await gather(
            fetch_wow_class.run(access_token=access_token), fetch_wow_specs.run(access_token=access_token)
        )

        # Esperando pra não tomar throtlle da api da blizz
        print(f"\nEsperando {DELAY} segundos para anti-throttle\n")
        await sleep(DELAY)

        print("\n4 - Fazendo um fetch nos dados de classes/specs dos jogadores...\n")
        pvp_data = await fetch_wow_media.run(access_token=access_token, pvp_data=pvp_data)

        print("\n5 - Salvando os dados coletados na base de dados...\n")
        await to_db(wow_classes=wow_classes, wow_specs=wow_specs, pvp_data=pvp_data)

    total = time() - inicio
    print(f"\nDemorou {total:.2f} segundos para realizar todas as requisições.\n")
