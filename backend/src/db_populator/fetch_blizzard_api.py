from asyncio import gather, sleep, create_task

from shared import Logger
from .constants import DELAY
from .fetcher import (
    get_latest_session,
    fetch_token,
    fetch_pvp_data,
    fetch_wow_classes,
    fetch_wow_specs,
    fetch_wow_media,
    save,
)

# For local development
from .utils import dump_data, read_data


async def fetch_blizzard_api(logger: Logger) -> None:

    latest_session = await get_latest_session()

    # Fetching the access token in order to make the other requests
    # response = await fetch_token(logger=logger)

    # Fetching pvp data, wow classes's data and wow specs's data concurrently
    # pvp_data, wow_classes, wow_specs = await gather(
    #     fetch_pvp_data(logger=logger, access_token=response.access_token, latest_session=latest_session),
    #     fetch_wow_classes(logger=logger, access_token=response.access_token),
    #     fetch_wow_specs(logger=logger, access_token=response.access_token),
    # )

    # await dump_data(pvp_data=pvp_data, wow_classes=wow_classes, wow_specs=wow_specs)
    pvp_data, wow_classes, wow_specs = await read_data()

    # Waiting so we don't get throttled
    # create_task(logger.info(f"Awaiting {DELAY} seconds in order to not get throttled."))
    # await sleep(DELAY)

    # Fetching the wow players's media
    # pvp_data = await fetch_wow_media(logger=logger, access_token=response.access_token, pvp_data=pvp_data)

    # create_task(save(logger=logger, pvp_data=pvp_data, wow_classes=wow_classes, wow_specs=wow_specs))
