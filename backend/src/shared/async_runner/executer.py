from typing import Awaitable, TypeVar

from .runner import Runner, _AwaitableReturnType


_AwaitableReturnType = TypeVar("_AwaitableReturnType")


def run_coroutine(awaitable: Awaitable[_AwaitableReturnType]) -> None:
    Runner(main_coroutine=awaitable)()
