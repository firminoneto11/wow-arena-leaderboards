from typing import Final

from sqlalchemy.ext.asyncio import create_async_engine
from decouple import config as get_env_var
from sqlalchemy import text

from api.apps.brackets import Sessions, BracketsEnum
from ..schemas import PvpDataSchema


async def get_latest_session() -> tuple[int, int]:

    DB_URL: Final[str] = get_env_var("DATABASE_URL").replace("{driver}", "+asyncpg")

    sql = f"SELECT id, session FROM {Sessions.Meta.tablename} ORDER BY session DESC LIMIT 1;"

    latest_session_id, latest_session = None, None

    engine = create_async_engine(DB_URL)

    async with engine.begin() as conn:
        result = await conn.execute(text(sql))
        if data_tuple := result.fetchone():
            latest_session_id, latest_session = data_tuple

    await engine.dispose()

    assert (
        type(latest_session_id) == int
    ), f"'latest_session_id' should be an integer. Got: '{type(latest_session_id)=}'"
    assert type(latest_session) == int, f"'latest_session' should be an integer. Got: '{type(latest_session)=}'"

    return latest_session_id, latest_session


def filter_pvp_data_list(data: list[PvpDataSchema]) -> list[list[PvpDataSchema]]:
    _2s, _3s, rbg = [], [], []

    for player in data:
        if player.bracket == BracketsEnum._2s.value:
            _2s.append(player)
        elif player.bracket == BracketsEnum._3s.value:
            _3s.append(player)
        elif player.bracket == BracketsEnum.rbg.value:
            rbg.append(player)

    return [_2s, _3s, rbg]
