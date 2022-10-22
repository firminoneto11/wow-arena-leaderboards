from typing import Coroutine

from .runner import Runner
from .event import Event


def run_coroutine(coroutine: Coroutine) -> None:
    return Runner(main_coroutine=coroutine)()
