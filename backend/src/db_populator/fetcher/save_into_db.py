from asyncio import to_thread as as_async
from enum import Enum

import pandas as pd

from db_populator.schemas import WowClassSchema, WowSpecsSchema, PvpDataSchema
from db_populator.fetcher.fetch_pvp_data import PvpDataType
from shared import Logger


class BracketsEnum(Enum):
    _2s = "2s"
    _3s = "3s"
    rbg = "rbg"


def _save_df(df: pd.DataFrame):
    # TODO: Create a SQLEngine
    # TODO: Save the data
    # TODO: Convert this process into a class
    print(df)


async def save_pvp_data(pvp_data: PvpDataType) -> None:
    df = {prop: [] for prop in PvpDataSchema.props()}
    df["bracket"] = []

    for bracket in pvp_data:
        bracket_val: str = BracketsEnum[bracket].value
        bracket_data: list[PvpDataSchema] = pvp_data[bracket]
        for el in bracket_data:
            el_dict = el.dict()
            for key in el_dict:
                df[key].append(el_dict[key])
            df["bracket"].append(bracket_val)

    df = pd.DataFrame(data=df).convert_dtypes()

    await as_async(_save_df, df=df)


async def save(
    logger: Logger, pvp_data: PvpDataType, wow_classes: list[WowClassSchema], wow_specs: list[WowSpecsSchema]
) -> None:
    await logger.info("Saving data into database...")

    await save_pvp_data(pvp_data=pvp_data)

    await logger.info("Data saved successfully!")
