from asyncio import get_running_loop
from typing import Coroutine
from functools import wraps

from shared import Event


def close_event_loop_after_execution(coroutine: Coroutine) -> None:
    @wraps(coroutine)
    async def inner(*args, **kwargs):
        coroutine_return = await coroutine(*args, **kwargs)
        get_running_loop().register_event(item=Event(name="cli-shutdown"))
        return coroutine_return

    return inner
