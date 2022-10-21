from typing import Final

from sqlalchemy.ext.asyncio import create_async_engine
from decouple import config as get_env_var
from sqlalchemy import MetaData
from databases import Database


class DataBaseEngine:
    DATABASE_URL: Final[str] = get_env_var("DATABASE_URL").replace("{driver}", "+asyncpg")
    metadata: MetaData
    db: Database

    def __init__(self) -> None:
        self.db = Database(self.DATABASE_URL)
        self.metadata = MetaData()

    async def create_all(self) -> None:
        engine = create_async_engine(self.DATABASE_URL)

        async with engine.begin() as conn:
            await conn.run_sync(self.metadata.create_all)

        await engine.dispose()


db_engine = DataBaseEngine()
