from asyncio import gather, sleep
from time import time

from shared.logging import AsyncLogger
from shared.decorators import async_timer

"""
async def to_db(wow_classes: List[WowClassesDt], wow_specs: List[WowSpecsDt], pvp_data: Dict[str, List[PvpDataDt]]):
    classes_tasks = []
    for wow_class in wow_classes:
        classes_tasks.append(create_wow_class(**wow_class.to_dict()))

    specs_tasks = []
    for wow_spec in wow_specs:
        specs_tasks.append(create_wow_spec(**wow_spec.to_dict()))

    pvp_data_tasks = []
    for key in pvp_data.keys():
        if key == "2s":
            bracket = await Brackets.objects.get(type="2v2")
            for pd in pvp_data[key]:
                pvp_data_tasks.append(create_pvp_data(pd=pd, bracket=bracket))
        elif key == "3s":
            bracket = await Brackets.objects.get(type="3v3")
            for pd in pvp_data[key]:
                pvp_data_tasks.append(create_pvp_data(pd=pd, bracket=bracket))
        else:
            bracket = await Brackets.objects.get(type="rbg")
            for pd in pvp_data[key]:
                pvp_data_tasks.append(create_pvp_data(pd=pd, bracket=bracket))

    await gather(*classes_tasks, *specs_tasks, *pvp_data_tasks)
"""


@async_timer(precision_level=5)
async def fetch_blizzard_api(*, logger: AsyncLogger) -> None:

    await logger.log("1: Fetching access token...")
    await sleep(1)
    await logger.log("Access token fetched successfully!")

    return

    # Checking if there were no errors in the first phase (Authentication)
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
