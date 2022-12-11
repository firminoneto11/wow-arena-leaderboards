from asyncio import create_task, gather, to_thread as as_async
from typing import Final, TypedDict, Callable
from datetime import datetime

from decouple import config as get_env_var
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import pandas as pd

from ..schemas import WowClassSchema, WowSpecsSchema, PvpDataSchema
from api.apps.core import WowClasses, WowSpecs, PvpData
from shared import Logger


class BaseKWargs(TypedDict):
    logger: Logger
    engine: Engine
    target: str


class CreateKWargs(BaseKWargs):
    data_frame: pd.DataFrame


class UpdateKWargs(BaseKWargs):
    temporary: str
    columns: list[str]
    compiler: Callable[[str, str, str], str]


class DeleteKWargs(BaseKWargs):
    ids: tuple[int]


def compile_insert_sql(target: str, columns: list[str], rows: list[tuple]) -> str:
    _columns = str(tuple(columns)).replace("'", "")
    query, values = f"INSERT INTO {target} {_columns} VALUES ", []
    for (idx, row) in enumerate(rows):
        clause = str(row).replace("None", "null")
        if idx:
            clause = ", " + clause
        values.append(clause)
    query += "".join(values) + ";"

    return query


def create(kwargs: CreateKWargs) -> None:
    data_frame, logger, target = kwargs["data_frame"], kwargs["logger"], kwargs["target"]

    data_frame["created_at"] = datetime.now().isoformat(sep=" ")
    data_frame["updated_at"] = datetime.now().isoformat(sep=" ")

    cols: list[str] = data_frame.columns.to_list()
    rows = [tuple([series[col] for col in cols]) for (_, series) in data_frame.iterrows()]

    logger.sInfo(f"Creating {len(rows)} rows from scratch into '{target}' table...")

    sql = compile_insert_sql(target=target, columns=cols, rows=rows)
    rows_affected: int = kwargs["engine"].execute(sql).rowcount

    logger.sInfo(f"Created {rows_affected} rows successfully into '{target}' table!")


def update(kwargs: UpdateKWargs) -> None:
    logger, temporary, target, columns, compiler = (
        kwargs["logger"],
        kwargs["temporary"],
        kwargs["target"],
        kwargs["columns"],
        kwargs["compiler"],
    )

    logger.sInfo(f"Updating '{target}' table...")

    sql = compiler(temporary, target, columns)
    rows_affected: int = kwargs["engine"].engine.execute(sql).rowcount

    logger.sInfo(f"{rows_affected} rows updated successfully on '{target}' table!")


def delete(kwargs: DeleteKWargs) -> None:
    ids, target, logger = kwargs["ids"], kwargs["target"], kwargs["logger"]

    logger.sInfo(f"Deleting {len(ids)} rows from '{target}' table...")

    if len(ids) > 1:
        sql = f"DELETE FROM {target} WHERE blizzard_id IN {ids};"
    else:
        sql = f"DELETE FROM {target} WHERE blizzard_id = {ids[0]};"

    rows_affected: int = kwargs["engine"].engine.execute(sql).rowcount

    logger.sInfo(f"{rows_affected} rows deleted successfully from '{target}' table!")


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

    async def _make_engine(self) -> None:
        self.engine = await as_async(create_engine, url=self.DB_URL)

    async def _close_engine(self) -> None:
        await as_async(self.engine.dispose)

    async def __call__(self) -> None:
        # Creating an engine to be used by threads
        await self._make_engine()

        wow_classes, wow_specs = await gather(self.save_wow_classes(), self.save_wow_specs())

        # await self.save_pvp_data(wow_classes_df=wow_classes, wow_specs_df=wow_specs)

        # Closing the engine
        await self._close_engine()

    async def save_wow_classes(self) -> pd.DataFrame:
        df = {prop: [] for prop in WowClassSchema.props()}

        for wc in self.wow_classes:
            el_dict = wc.dict()
            for key in el_dict:
                df[key].append(el_dict[key])

        df = pd.DataFrame(data=df).convert_dtypes()

        return await self.save(
            df=df,
            temporary_table=WowClasses.Meta.tablename + "_temp",
            target_table=WowClasses.Meta.tablename,
            which="classes_n_specs",
        )

    async def save_wow_specs(self) -> pd.DataFrame:
        df = {prop: [] for prop in WowSpecsSchema.props()}

        for wc in self.wow_specs:
            el_dict = wc.dict()
            for key in el_dict:
                df[key].append(el_dict[key])

        df = pd.DataFrame(data=df).convert_dtypes()

        return await self.save(
            df=df,
            temporary_table=WowSpecs.Meta.tablename + "_temp",
            target_table=WowSpecs.Meta.tablename,
            which="classes_n_specs",
        )

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
                elif key == "wow_spec":
                    df[key].append(wow_specs_map.get(player.wow_spec))
                elif key == "realm":
                    df[key].append(player.realm.title())
                else:
                    df[key].append(data_dict[key])

        df = pd.DataFrame(data=df).convert_dtypes()
        df.replace({pd.NA: None}, inplace=True)

        await self.save(
            df=df,
            temporary_table=PvpData.Meta.tablename + "_temp",
            target_table=PvpData.Meta.tablename,
            which="pvp_data",
        )

    async def save(self, df: pd.DataFrame, temporary_table: str, target_table: str, which: str) -> pd.DataFrame:
        kwargs = {"temporary_table": temporary_table, "target_table": target_table, "df": df}
        match which:
            case "classes_n_specs":
                return await as_async(self._save_classes_n_specs, **kwargs)
            case "pvp_data":
                return await as_async(self._save_pvp_data, **kwargs)

    def _save_classes_n_specs(self, df: pd.DataFrame, temporary_table: str, target_table: str) -> pd.DataFrame:
        """Saves the data related to WowClasses and WowSpecs instances"""

        read_target_table_sql = f"SELECT * FROM {target_table} ORDER BY blizzard_id ASC;"

        def compile_update_sql(temporary: str, target: str, columns: list[str]) -> str:
            query, fields_to_update = f"UPDATE {target} target SET ", []
            for (idx, col) in enumerate(columns):
                clause = f"{col} = temporary.{col}"
                if idx:
                    clause = ", " + clause
                fields_to_update.append(clause)
            fields_to_update.append(f", updated_at = '{datetime.now().isoformat(sep=' ')}'")
            fields_to_update = "".join(fields_to_update)
            query += fields_to_update
            query += f" FROM {temporary} temporary WHERE target.blizzard_id = temporary.blizzard_id;"

            return query

        if self.engine.execute(f"SELECT COUNT(*) FROM {target_table};").fetchone()[0]:

            # Changing the index to be the blizzard_id field
            df_from_api = df.copy()
            df_from_api.set_index("blizzard_id", inplace=True)

            # Creating a DataFrame based on the data that already is saved on DB
            df_from_db = (
                pd.read_sql(sql=read_target_table_sql, con=self.engine, index_col="blizzard_id")
                .drop(columns=["id", "created_at", "updated_at"])
                .convert_dtypes()
                .replace({pd.NA: None})
            )

            # Creating a list of 'blizzard_id' that are in the api data, but aren't in the database, meaning that they'll have to be
            # INSERTED
            if to_create := [idx for idx in df_from_api.index.tolist() if idx not in df_from_db.index.tolist()]:
                df_to_insert = df_from_api.loc[to_create].reset_index()

                # Creating the data in the target table
                kwargs = {
                    "logger": self.logger,
                    "engine": self.engine,
                    "target": target_table,
                    "data_frame": df_to_insert,
                }
                create(kwargs=kwargs)

                # Dropping the data created from 'df_from_api' data frame because it won't be needed anymore
                df_from_api.drop(labels=to_create, inplace=True)

                del df_to_insert
                del to_create

            has_to_update, to_delete = False, []

            for (blizzard_id, row) in df_from_db.iterrows():
                try:
                    series_from_api: pd.Series = df_from_api.loc[blizzard_id]
                except KeyError:
                    # If 'KeyError' is raised, that means that the given 'blizzard_id' was removed from the API, therefore, has to be
                    # removed from here as well
                    to_delete.append(int(blizzard_id))
                    continue

                if not has_to_update:
                    series_from_db = row.convert_dtypes().replace({pd.NA: None})
                    if not series_from_api.equals(other=series_from_db):
                        has_to_update = True

            # Checking if there are any items to be deleted and doing so if true
            if to_delete:

                # Deleting the data from the target table
                kwargs = {
                    "ids": tuple(to_delete),
                    "target": target_table,
                    "logger": self.logger,
                    "engine": self.engine,
                }
                delete(kwargs=kwargs)

                del to_delete

            # If at least one of them changed, all rows will be updated!
            if has_to_update:
                df_from_api.reset_index(inplace=True)
                df_from_api.index += 1

                kwargs = {
                    "logger": self.logger,
                    "engine": self.engine,
                    "target": target_table,
                    "temporary": temporary_table,
                    "columns": df_from_api.columns.to_list(),
                    "compiler": compile_update_sql,
                }

                # Updating the target table and dropping the temporary table
                df_from_api.to_sql(
                    con=self.engine, method="multi", name=temporary_table, if_exists="replace", index="id"
                )
                update(kwargs=kwargs)
                self.engine.execute(f"DROP TABLE {temporary_table};")

        else:
            # Creating the data in the target table
            kwargs = {"logger": self.logger, "engine": self.engine, "target": target_table, "data_frame": df.copy()}
            create(kwargs=kwargs)

        return pd.read_sql(sql=read_target_table_sql, con=self.engine)

    def _save_pvp_data(self, df: pd.DataFrame, temporary_table: str, target_table: str) -> pd.DataFrame:

        read_target_table_sql = f"SELECT * FROM {target_table} ORDER BY blizzard_id ASC;"

        def compile_update_sql(temporary: str, target: str, columns: list[str]) -> str:
            query, fields_to_update = f"UPDATE {target} target SET ", []
            for (idx, col) in enumerate(columns):
                clause = f"{col} = temporary.{col}"
                if idx:
                    clause = ", " + clause
                fields_to_update.append(clause)
            fields_to_update.append(f", updated_at = '{datetime.now().isoformat(sep=' ')}'")
            fields_to_update = "".join(fields_to_update)
            query += fields_to_update
            query += (
                f" FROM {temporary} temporary WHERE "
                f"target.blizzard_id = temporary.blizzard_id AND target.bracket = temporary.bracket;"
            )

            return query

        if self.engine.execute(f"SELECT COUNT(*) FROM {target_table};").fetchone()[0]:

            # Changing the index to be the blizzard_id field
            df_from_api = df.copy()
            df_from_api.set_index("blizzard_id", inplace=True)

            # Creating a DataFrame based on the data that already is saved on DB
            df_from_db = (
                pd.read_sql(sql=read_target_table_sql, con=self.engine, index_col="blizzard_id")
                .drop(columns=["id", "created_at", "updated_at"])
                .convert_dtypes()
                .replace({pd.NA: None})
            )

            # Saving the data from the api into a temporary table
            # df_copy = df.copy()
            # df_copy.index += 1
            # df_copy.to_sql(con=self.engine, method="multi", name=temporary_table, if_exists="replace", index="id")
            # df_copy.set_index("blizzard_id", inplace=True)

            # Creating a DataFrame based on the data that already is saved on DB
            # in_db_already = (
            #     pd.read_sql(sql=read_target_table_sql, con=self.engine, index_col="id")
            #     .drop(columns=["created_at", "updated_at"])
            #     .convert_dtypes()
            #     .replace({pd.NA: None})
            # )

            # TODO: Refactor this method for PvpData model

            has_to_update, to_delete = False, []

            for (blizzard_id, row) in df_from_db.iterrows():
                try:
                    series_from_api: pd.Series = df_from_api.loc[blizzard_id]
                except KeyError:
                    # If 'KeyError' is raised, that means that the given 'blizzard_id' was removed from the API, therefore, has to be
                    # removed from here as well
                    to_delete.append(int(blizzard_id))
                    continue

                if not has_to_update:
                    series_in_db = row.convert_dtypes().replace({pd.NA: None})
                    if not series_from_api.equals(other=series_in_db):
                        has_to_update = True

            # Checking if there are any items to be deleted
            if to_delete:
                # delete(ids=tuple(to_delete), table=original_table)
                del to_delete

            # If at least one of them changed, all rows will be updated!
            if has_to_update:
                cols = df_from_api.reset_index().columns.to_list()
                # update(cols=cols, original=original_table, temp=temp_table)
                del cols

            # Creating a list of 'blizzard_id' that are in the api data, but aren't in the database, meaning that they'll have to be
            # INSERTED
            if to_create := [idx for idx in df_from_api.index.tolist() if idx not in df_from_db.index.tolist()]:
                ids = to_create.copy()
                to_create = df_from_api.loc[to_create]
                to_create.reset_index(inplace=True)
                # create(data_frame=to_create, table=original_table)
                df_from_api.drop(labels=ids, inplace=True)
                del to_create
                del ids

            # -- | --

        else:
            # Creating the data in the target table
            kwargs = {"logger": self.logger, "engine": self.engine, "target": target_table, "data_frame": df.copy()}
            create(kwargs=kwargs)

        return pd.read_sql(sql=read_target_table_sql, con=self.engine)


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
