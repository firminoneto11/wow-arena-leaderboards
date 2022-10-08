from asyncio import create_task, gather, to_thread as as_async
from datetime import datetime
from typing import Final
from enum import Enum

from decouple import config as get_env_var
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import pandas as pd

from db_populator.schemas import WowClassSchema, WowSpecsSchema, PvpDataSchema
from db_populator.fetcher.fetch_pvp_data import PvpDataType
from shared import Logger


class BracketsEnum(Enum):
    _2s = "2s"
    _3s = "3s"
    rbg = "rbg"


class ToDatabase:

    engine: Engine
    logger: Logger
    pvp_data: PvpDataType
    wow_classes: list[WowClassSchema]
    wow_specs: list[WowSpecsSchema]
    DB_URL: Final[str] = get_env_var("DATABASE_URL").replace("asyncpg", "psycopg2")

    def __init__(
        self, logger: Logger, pvp_data: PvpDataType, wow_classes: list[WowClassSchema], wow_specs: list[WowSpecsSchema]
    ) -> None:
        self.logger = logger
        self.pvp_data = pvp_data
        self.wow_classes = wow_classes
        self.wow_specs = wow_specs

    async def __call__(self) -> None:
        # Creating an engine to be used by threads
        await self._make_engine()

        # await gather(self.save_wow_classes(), self.save_wow_specs())
        await self.save_wow_classes()

        # Closing the engine
        await self._close_engine()

    async def _make_engine(self) -> None:
        url = self.DB_URL

        def make_engine() -> Engine:
            return create_engine(url=url)

        self.engine = await as_async(make_engine)

    async def _close_engine(self) -> None:
        engine = self.engine

        def close_engine() -> None:
            return engine.dispose()

        return await as_async(close_engine)

    def _compile_update_sql(self, temp_table: str, original_table: str, cols: list[str]) -> str:
        sql = f"UPDATE {original_table} ot SET "
        fields_to_update = []
        for (idx, col) in enumerate(cols):
            clause = f"{col} = tt.{col}"
            if idx:
                clause = ", " + clause
            if col != "created_at":
                fields_to_update.append(clause)
        fields_to_update = "".join(fields_to_update)
        sql += fields_to_update

        _cols = ", ".join(cols)
        subquery = f"(SELECT {_cols} FROM {temp_table}) tt"

        sql += f" FROM {subquery} WHERE ot.blizzard_id = tt.blizzard_id;"

        return sql

    def _compile_insert_sql(self, table: str, cols: list[str], rows: list[tuple]) -> str:
        _cols = str(tuple(cols)).replace("'", "")
        sql = f"INSERT INTO {table} {_cols} VALUES "
        values = []
        for (idx, row) in enumerate(rows):
            clause = str(row)
            if idx:
                clause = ", " + clause
            values.append(clause)
        sql += "".join(values) + ";"

        return sql

    def _save(self, df: pd.DataFrame, temp_table: str, original_table: str) -> pd.DataFrame:
        def create(data_frame: pd.DataFrame, table: str) -> None:
            data_frame["created_at"] = datetime.now().isoformat(sep=" ")
            data_frame["updated_at"] = datetime.now().isoformat(sep=" ")

            cols: list[str] = data_frame.columns.to_list()
            rows = [tuple([series[col] for col in cols]) for (_, series) in data_frame.iterrows()]

            self.logger.sInfo(f"Creating {len(rows)} rows from scratch into '{table}' table...")

            insert_sql = self._compile_insert_sql(table=table, cols=cols, rows=rows)
            rows_affected = self.engine.execute(insert_sql).rowcount

            self.logger.sInfo(f"Created {rows_affected} rows successfully into '{table}' table!")

        def update(data_frame: pd.DataFrame, tt: str, ot: str) -> None:
            data_frame["updated_at"] = datetime.now().isoformat(sep=" ")
            cols: list[str] = data_frame.columns.to_list()

            self.logger.sInfo(f"Updating '{ot}' table...")

            update_sql = self._compile_update_sql(temp_table=tt, original_table=ot, cols=cols)
            rows_affected = self.engine.execute(update_sql).rowcount

            self.logger.sInfo(f"'{ot}' table updated successfully on {rows_affected} rows!")

        def delete(ids: tuple[int], table: str) -> None:
            self.logger.info(f"Deleting {len(ids)} rows from '{table}' table...")
            rows_affected = self.engine.execute(f"DELETE FROM {table} WHERE blizzard_id IN {ids};").rowcount
            self.logger.info(f"{rows_affected} rows deleted successfully from '{table}' table!")

        sql = f"SELECT * FROM {original_table} ORDER BY blizzard_id ASC;"
        has_data: int = self.engine.execute(f"SELECT COUNT(*) FROM {original_table};").fetchone()[0]

        if has_data:
            # Saving the data from the api into a temporary table
            df_copy = df.copy()
            df_copy["created_at"] = datetime.now()
            df_copy["updated_at"] = datetime.now()
            df_copy.index += 1
            df_copy.to_sql(con=self.engine, method="multi", name=temp_table, if_exists="replace", index="id")

            df_copy.set_index("blizzard_id", inplace=True)
            df_copy.drop(columns=["created_at", "updated_at"], inplace=True)

            # Creating a DataFrame based on the data that already is saved on DB
            in_db_already = (
                pd.read_sql(sql=sql, con=self.engine, index_col="blizzard_id")
                .drop(columns=["id", "created_at", "updated_at"])
                .convert_dtypes()
            )

            # Creating a list of 'blizzard_id' that are in the api data, but aren't in the database, meaning that they'll have to be
            # INSERTED
            if to_create := [idx for idx in df_copy.index.tolist() if idx not in in_db_already.index.tolist()]:
                ids = to_create.copy()
                to_create = df_copy.loc[to_create]
                to_create.reset_index(inplace=True)
                create(data_frame=to_create, table=original_table)
                df_copy.drop(labels=ids, inplace=True)

            to_update = []
            to_delete = []

            # TODO: Test 'delete' function
            # TODO: Create a DataFrame to be updated instead of indexes

            for (blizzard_id, row) in in_db_already.iterrows():
                series_in_db = row.convert_dtypes()
                try:
                    series_from_api: pd.Series = df_copy.loc[blizzard_id]
                except:
                    to_delete.append(int(blizzard_id))
                else:
                    if not series_from_api.equals(other=series_in_db):
                        to_update.append(blizzard_id)

            # if to_delete:
            #     delete(ids=tuple(to_delete), table=original_table)

        else:
            create(data_frame=df.copy(), table=original_table)

        return pd.read_sql(sql=sql, con=self.engine, index_col="id")

    async def save(self, df: pd.DataFrame, temp_table: str, original_table: str) -> pd.DataFrame:
        return await as_async(self._save, df=df, temp_table=temp_table, original_table=original_table)

    async def save_wow_classes(self) -> None:
        df = {prop: [] for prop in WowClassSchema.props()}

        for wc in self.wow_classes:
            el_dict = wc.dict()
            for key in el_dict:
                df[key].append(el_dict[key])

        df = pd.DataFrame(data=df).convert_dtypes()

        await self.save(df=df, temp_table="wow_classes_temp", original_table="wow_classes")

    async def save_wow_specs(self) -> None:
        df = {prop: [] for prop in WowSpecsSchema.props()}

        for wc in self.wow_specs:
            el_dict = wc.dict()
            for key in el_dict:
                df[key].append(el_dict[key])

        df = pd.DataFrame(data=df).convert_dtypes()

        await self.save(df=df, temp_table="wow_specs_temp", original_table="wow_specs")

    async def save_pvp_data(self) -> None:
        df = {prop: [] for prop in PvpDataSchema.props()}
        df["bracket"] = []

        for bracket in self.pvp_data:
            bracket_val: str = BracketsEnum[bracket].value
            bracket_data: list[PvpDataSchema] = self.pvp_data[bracket]
            for el in bracket_data:
                el_dict = el.dict()
                for key in el_dict:
                    df[key].append(el_dict[key])
                df["bracket"].append(bracket_val)

        df = pd.DataFrame(data=df).convert_dtypes()

        # await self.save(df=df, temp_table="pvp_data_temp")


async def save(
    logger: Logger, pvp_data: PvpDataType, wow_classes: list[WowClassSchema], wow_specs: list[WowSpecsSchema]
) -> None:
    create_task(logger.info("Saving data into database..."))
    handler = ToDatabase(logger=logger, pvp_data=pvp_data, wow_classes=wow_classes, wow_specs=wow_specs)
    await handler()
    await logger.info("Data saved successfully!")
