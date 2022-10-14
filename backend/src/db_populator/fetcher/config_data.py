from typing import Final

from sqlalchemy.ext.asyncio import create_async_engine
from decouple import config as get_env_var
from sqlalchemy import text

from apps.brackets.models import Sessions


async def get_latest_session() -> int:

    DB_URL: Final[str] = get_env_var("DATABASE_URL").replace("{driver}", "+asyncpg")

    sql = f"SELECT session FROM {Sessions.tablename} ORDER BY session DESC LIMIT 1;"

    latest_session = None

    engine = create_async_engine(DB_URL)
    async with engine.begin() as conn:
        result = await conn.execute(text(sql))
        if latest_session := result.fetchone():
            latest_session = latest_session[0]
    await engine.dispose()

    # TODO: Find a clean way to save the latest sessions

    # assert type(latest_session) == int, f"'latest_session' should be an integer. Got: '{type(latest_session)=}'"

    return 33
