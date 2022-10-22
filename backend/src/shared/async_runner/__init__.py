from .runner import Runner
from .events import emit_event
from .types import _Coroutine


def run_coroutine(coroutine: type[_Coroutine]):
    return Runner(main_coroutine=coroutine)()
