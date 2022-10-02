from asyncio import gather, sleep

from shared import Logger
from .schemas import PvpDataSchema, WowClassSchema, WowSpecsSchema
from .constants import DELAY
from .fetcher import (
    fetch_token,
    fetch_pvp_data,
    fetch_wow_classes,
    fetch_wow_specs,
    fetch_wow_media,
)

# For local development
from .utils import dump_data, read_data


async def fetch_blizzard_api(logger: Logger) -> None:

    # Fetching the access token in order to make the other requests
    # response = await fetch_token(logger=logger)

    # Fetching pvp data, wow classes's data and wow specs's data concurrently
    # pvp_data, wow_classes, wow_specs = await gather(
    #     fetch_pvp_data(logger=logger, access_token=response.access_token),
    #     fetch_wow_classes(logger=logger, access_token=response.access_token),
    #     fetch_wow_specs(logger=logger, access_token=response.access_token),
    # )

    # await dump_data(pvp_data=pvp_data, wow_classes=wow_classes, wow_specs=wow_specs)
    pvp_data, wow_classes, wow_specs = await read_data()

    # Waiting so we dont get throttled
    # await logger.info(f"Awaiting {DELAY} seconds in order to not get throttled.")
    # await sleep(DELAY)

    access_token = "USwgFVBttgL26SuCIYPWQ442ivh62i9Mvj"

    # Fetching the wow players's media
    pvp_data = await fetch_wow_media(logger=logger, access_token=access_token, pvp_data=pvp_data)

    return

    print("\n5 - Salvando os dados coletados na base de dados...\n")
    await to_db(wow_classes=wow_classes, wow_specs=wow_specs, pvp_data=pvp_data)
