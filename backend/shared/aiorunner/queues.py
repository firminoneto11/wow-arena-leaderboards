from asyncio import Queue
from typing import Self

from .events import Event


class EventsQueue:

    _instance: Self
    _queue: Queue[Event]

    def __new__(cls, *args, **kwargs) -> Self:
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._queue = Queue()
        return cls._instance

    @property
    @classmethod
    def queue(cls) -> Queue[Event]:
        return cls()._queue
