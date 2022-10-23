from typing import TypeVar, Awaitable, ParamSpec, Callable
from functools import wraps

from shared import emit_event, EventTypes


_ParamTypes = ParamSpec("_ParamTypes")
_AwaitableReturnType = TypeVar("_AwaitableReturnType")


def close_event_loop_after_execution(
    callable_that_returns_an_awaitable: Callable[_ParamTypes, Awaitable[_AwaitableReturnType]]
) -> Callable[_ParamTypes, Awaitable[_AwaitableReturnType]]:
    """This decorator simply make sure that the main event loop is closed after the coroutine finishes it's execution."""

    @wraps(callable_that_returns_an_awaitable)
    async def decorator(*args: _ParamTypes.args, **kwargs: _ParamTypes.kwargs) -> _AwaitableReturnType:
        coroutine_return = await callable_that_returns_an_awaitable(*args, **kwargs)
        emit_event(name=EventTypes.CLI_SHUTDOWN.name)
        return coroutine_return

    return decorator
