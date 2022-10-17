from asyncio import create_task, gather, to_thread as as_async
from datetime import datetime
from typing import Final

from decouple import config as get_env_var
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import pandas as pd, numpy as np

from db_populator.schemas import WowClassSchema, WowSpecsSchema, PvpDataSchema
from apps.brackets.models import BracketsEnum, WowClasses, WowSpecs
from shared import Logger


class ToDatabase:

    engine: Engine
    logger: Logger
    latest_session_id: int
    pvp_data: list[PvpDataSchema]
    wow_classes: list[WowClassSchema]
    wow_specs: list[WowSpecsSchema]
    DB_URL: Final[str] = get_env_var("DATABASE_URL").replace("{driver}", "+psycopg2")

    def __init__(
        self,
        logger: Logger,
        pvp_data: list[PvpDataSchema],
        wow_classes: list[WowClassSchema],
        wow_specs: list[WowSpecsSchema],
        latest_session_id: int,
    ) -> None:
        self.logger = logger
        self.pvp_data = pvp_data
        self.wow_classes = wow_classes
        self.wow_specs = wow_specs
        self.latest_session_id = latest_session_id

    async def __call__(self) -> None:
        # Creating an engine to be used by threads
        await self._make_engine()

        wow_classes, wow_specs = await gather(self.save_wow_classes(), self.save_wow_specs())

        await self.save_pvp_data(wow_classes_df=wow_classes, wow_specs_df=wow_specs)

        # Closing the engine
        await self._close_engine()

    async def _make_engine(self) -> None:
        def make_engine() -> Engine:
            return create_engine(url=self.DB_URL)

        self.engine = await as_async(make_engine)

    async def _close_engine(self) -> None:
        def close_engine() -> None:
            return self.engine.dispose()

        return await as_async(close_engine)

    def _compile_update_sql(self, temp_table: str, original_table: str, cols: list[str]) -> str:
        sql = f"UPDATE {original_table} ot SET "
        fields_to_update = []
        for (idx, col) in enumerate(cols):
            clause = f"{col} = tt.{col}"
            if idx:
                clause = ", " + clause
            fields_to_update.append(clause)
        fields_to_update.append(f", updated_at = '{datetime.now().isoformat(sep=' ')}'")
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

        def update(cols: list[str], tt: str, ot: str) -> None:

            self.logger.sInfo(f"Updating '{ot}' table...")

            update_sql = self._compile_update_sql(temp_table=tt, original_table=ot, cols=cols)
            rows_affected = self.engine.execute(update_sql).rowcount

            self.logger.sInfo(f"{rows_affected} rows updated successfully on '{ot}' table!")

        def delete(ids: tuple[int], table: str) -> None:

            self.logger.sInfo(f"Deleting {len(ids)} rows from '{table}' table...")

            if len(ids) > 1:
                delete_sql = f"DELETE FROM {table} WHERE blizzard_id IN {ids};"
            else:
                delete_sql = f"DELETE FROM {table} WHERE blizzard_id = {ids[0]};"

            rows_affected = self.engine.execute(delete_sql).rowcount

            self.logger.sInfo(f"{rows_affected} rows deleted successfully from '{table}' table!")

        sql = f"SELECT * FROM {original_table} ORDER BY blizzard_id ASC;"

        if self.engine.execute(f"SELECT COUNT(*) FROM {original_table};").fetchone()[0]:
            # Saving the data from the api into a temporary table
            df_copy = df.copy()
            df_copy.index += 1
            df_copy.to_sql(con=self.engine, method="multi", name=temp_table, if_exists="replace", index="id")
            df_copy.set_index("blizzard_id", inplace=True)

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
                del to_create
                del ids

            has_to_update = False
            to_delete = []

            for (blizzard_id, row) in in_db_already.iterrows():
                try:
                    series_from_api: pd.Series = df_copy.loc[blizzard_id]
                except KeyError:
                    # If 'KeyError' is raised, that means that the given 'blizzard_id' was removed from the API, therefore, has to be
                    # removed from here as well
                    to_delete.append(int(blizzard_id))
                    continue

                if not has_to_update:
                    series_in_db = row.convert_dtypes()
                    if not series_from_api.equals(other=series_in_db):
                        has_to_update = True

            # If there's at least one of them changed, all rows will be updated!
            if has_to_update:
                cols = df_copy.reset_index().columns.to_list()
                update(cols=cols, ot=original_table, tt=temp_table)

            if to_delete:
                delete(ids=tuple(to_delete), table=original_table)

            del to_delete

        else:
            create(data_frame=df.copy(), table=original_table)

        return pd.read_sql(sql=sql, con=self.engine)

    async def save(self, df: pd.DataFrame, temp_table: str, original_table: str) -> pd.DataFrame:
        return await as_async(self._save, df=df, temp_table=temp_table, original_table=original_table)

    async def save_wow_classes(self) -> pd.DataFrame:
        df = {prop: [] for prop in WowClassSchema.props()}

        for wc in self.wow_classes:
            el_dict = wc.dict()
            for key in el_dict:
                df[key].append(el_dict[key])

        df = pd.DataFrame(data=df).convert_dtypes()

        return await self.save(df=df, temp_table=WowClasses.tablename + "_temp", original_table=WowClasses.tablename)

    async def save_wow_specs(self) -> pd.DataFrame:
        df = {prop: [] for prop in WowSpecsSchema.props()}

        for wc in self.wow_specs:
            el_dict = wc.dict()
            for key in el_dict:
                df[key].append(el_dict[key])

        df = pd.DataFrame(data=df).convert_dtypes()

        return await self.save(df=df, temp_table=WowSpecs.tablename + "_temp", original_table=WowSpecs.tablename)

    async def save_pvp_data(self, wow_classes_df: pd.DataFrame, wow_specs_df: pd.DataFrame) -> None:

        wow_classes_map = wow_classes_df.copy()[["blizzard_id", "id"]].set_index("blizzard_id")
        wow_classes_map = {int(el[0]): int(el[1]) for el in wow_classes_map.iterrows()}

        wow_specs_map = wow_specs_df.copy()[["blizzard_id", "id"]].set_index("blizzard_id")
        wow_specs_map = {int(el[0]): int(el[1]) for el in wow_specs_map.iterrows()}

        df = {prop: [] for prop in PvpDataSchema.props()}

        for player in self.pvp_data:
            data_dict = player.dict()
            for key in data_dict:
                if key == "session":
                    df[key].append(self.latest_session_id)
                elif key == "wow_class":
                    df[key].append(wow_classes_map.get(player.wow_class))
                elif key == "wow_specs":
                    df[key].append(wow_specs_map.get(player.wow_spec))
                elif key == "realm":
                    df[key].append(player.realm.title())
                else:
                    df[key].append(data_dict[key])

        df = pd.DataFrame(data=df).convert_dtypes()

        # TODO: Find out how to replace <NA> for None

        def _inner(series: pd.Series):
            name = series.name
            if series.hasnans:
                indexes = series.loc[series.isnull()].index.to_list()
                for idx in indexes:
                    df[name][idx] = None
                    print(df[name][idx])

        df.apply(_inner)

        print(df)

        # await self.save(df=df, temp_table="pvp_data_temp")


async def save(
    logger: Logger,
    pvp_data: list[PvpDataSchema],
    wow_classes: list[WowClassSchema],
    wow_specs: list[WowSpecsSchema],
    latest_session_id: int,
) -> None:
    create_task(logger.info("Saving data into database..."))
    handler = ToDatabase(
        logger=logger,
        pvp_data=pvp_data,
        wow_classes=wow_classes,
        wow_specs=wow_specs,
        latest_session_id=latest_session_id,
    )
    await handler()
    await logger.info("Data saved successfully!")
