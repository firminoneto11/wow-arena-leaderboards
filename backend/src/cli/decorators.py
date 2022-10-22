from typing import Callable, TypeVar as Generic
from typing import Coroutine
from functools import wraps

from shared import emit_event


_Coroutine = Generic("_Coroutine", bound=Coroutine)
_Callable = Generic("_Callable", bound=Callable)


def close_event_loop_after_execution(coroutine: type[_Callable]) -> type[_Coroutine]:
    @wraps(coroutine)
    async def inner(*args, **kwargs):
        coroutine_return = await coroutine(*args, **kwargs)
        emit_event(name="cli-shutdown")
        return coroutine_return

    return inner
