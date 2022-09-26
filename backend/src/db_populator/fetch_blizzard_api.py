from asyncio import gather, sleep

from shared import Logger
from .fetcher import fetch_token, fetch_pvp_data

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


async def fetch_blizzard_api(*, logger: Logger) -> None:

    response = await fetch_token(logger=logger)

    # Checking if the first phase (Authentication) was successfully completed
    if response is not None:

        pvp_data = await fetch_pvp_data(logger=logger, access_token=response.access_token)

        return

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
