from database import db_engine


class DbConnection:
    async def __aenter__(self, *args, **kwargs) -> None:
        if not db_engine.db.is_connected:
            await db_engine.db.connect()

    async def __aexit__(self, *args, **kwargs) -> None:
        if db_engine.db.is_connected:
            await db_engine.db.disconnect()
