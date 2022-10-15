from typing import Final

from sqlalchemy.ext.asyncio import create_async_engine
from decouple import config as get_env_var
from sqlalchemy import text

from apps.brackets.models import Sessions


async def get_latest_session() -> tuple[int, int]:

    DB_URL: Final[str] = get_env_var("DATABASE_URL").replace("{driver}", "+asyncpg")

    sql = f"SELECT id, session FROM {Sessions.tablename} ORDER BY session DESC LIMIT 1;"

    latest_session_id, latest_session = None, None

    engine = create_async_engine(DB_URL)

    async with engine.begin() as conn:
        result = await conn.execute(text(sql))
        if data_tuple := result.fetchone():
            latest_session_id, latest_session = data_tuple

    await engine.dispose()

    # TODO: Find a clean way to save the latest sessions

    # assert (
    #     type(latest_session_id) == int
    # ), f"'latest_session_id' should be an integer. Got: '{type(latest_session_id)=}'"
    # assert type(latest_session) == int, f"'latest_session' should be an integer. Got: '{type(latest_session)=}'"

    return 1, 33
    return latest_session_id, latest_session
