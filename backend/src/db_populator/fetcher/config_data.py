from asyncio import gather
from typing import Final

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from decouple import config as get_env_var

from apps.brackets.models import Brackets, BracketsEnum, Sessions


async def get_config_data() -> tuple[int, list[str]]:
    DB_URL: Final[str] = get_env_var("DATABASE_URL").replace("{driver}", "+asyncpg")
    engine = create_async_engine(DB_URL)

    brackets: list[str] = [BracketsEnum[el].value for el in BracketsEnum._member_names_]

    count_brackets_sql = f"SELECT COUNT(*) FROM {Brackets.tablename} WHERE name IN {tuple(brackets)};"
    latest_session_sql = f"SELECT session FROM {Sessions.tablename} ORDER BY session DESC LIMIT 1;"

    brackets_count, latest_session = None, None

    async with engine.begin() as conn:
        brackets_result, session_result = await gather(
            conn.execute(text(count_brackets_sql)),
            conn.execute(text(latest_session_sql)),
        )

        if brackets_count := brackets_result.fetchone():
            brackets_count = brackets_count[0]

        if latest_session := session_result.fetchone():
            latest_session = latest_session[0]

    await engine.dispose()

    # TODO: Find a clean way to save the latest sessions

    # assert (brackets_count == len(brackets)) and (latest_session is not None), (
    #     f"'brackets_count' should be equal to {len(brackets)} and 'latest_session' should be and integer. "
    #     f"Got: '{brackets_count=}' and '{latest_session=}'"
    # )

    return 33, brackets
