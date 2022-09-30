from asyncio import gather, sleep

from shared import Logger
from .constants import DELAY
from .fetcher import fetch_token, fetch_pvp_data, fetch_wow_classes, fetch_wow_specs


async def fetch_blizzard_api(*, logger: Logger) -> None:

    response = await fetch_token(logger=logger)

    pvp_data, wow_classes = await gather(
        fetch_pvp_data(logger=logger, access_token=response.access_token),
        fetch_wow_classes(logger=logger, access_token=response.access_token),
        # fetch_wow_specs(logger=logger, access_token=response.access_token),
    )

    # Waiting so we dont get throttled
    await logger.info(f"Awaiting {DELAY} seconds in order to not get throttled.")
    await sleep(DELAY)

    return

    print("\n4 - Fazendo um fetch nos dados de classes/specs dos jogadores...\n")
    pvp_data = await fetch_wow_media.run(access_token=access_token, pvp_data=pvp_data)

    print("\n5 - Salvando os dados coletados na base de dados...\n")
    await to_db(wow_classes=wow_classes, wow_specs=wow_specs, pvp_data=pvp_data)
