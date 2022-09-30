from asyncio import gather, sleep

from shared import Logger
from .constants import DELAY
from .fetcher import (
    fetch_token,
    fetch_pvp_data,
    fetch_wow_classes,
    fetch_wow_specs,
    fetch_wow_media,
)


async def fetch_blizzard_api(*, logger: Logger) -> None:

    response = await fetch_token(logger=logger)

    kwargs = {"logger": logger, "access_token": response.access_token}

    # Fetching pvp data, wow classes's data and wow specs's data concurrently
    pvp_data, wow_classes, wow_specs = await gather(
        fetch_pvp_data(**kwargs), fetch_wow_classes(**kwargs), fetch_wow_specs(**kwargs)
    )

    # Waiting so we dont get throttled
    await logger.info(f"Awaiting {DELAY} seconds in order to not get throttled.")
    await sleep(DELAY)

    kwargs["pvp_data"] = pvp_data

    # Fetching the wow players's media
    pvp_data = await fetch_wow_media(**kwargs)

    return

    print("\n5 - Salvando os dados coletados na base de dados...\n")
    await to_db(wow_classes=wow_classes, wow_specs=wow_specs, pvp_data=pvp_data)
