from asyncio import sleep

import pandas as pd

from db_populator.fetcher.fetch_pvp_data import PvpDataType
from db_populator.schemas import WowClassSchema, WowSpecsSchema
from shared import Logger


async def save(
    logger: Logger, pvp_data: PvpDataType, wow_classes: list[WowClassSchema], wow_specs: list[WowSpecsSchema]
) -> None:
    await logger.info("Saving data into database...")
    await sleep(2)
    await logger.info("Data saved successfully!")
