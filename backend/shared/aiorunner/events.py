from dataclasses import dataclass
from typing import Literal

from .enums import EventTypes


@dataclass
class Event:
    name: Literal[EventTypes.CLI_SHUTDOWN]

    def emit(self) -> None:
        from .queues import EventsQueue

        EventsQueue.queue.put_nowait(item=self)
