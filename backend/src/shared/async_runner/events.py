from dataclasses import dataclass
from asyncio import Queue
from enum import Enum


class EventTypes(Enum):
    CLI_SHUTDOWN = "cli-shutdown"


@dataclass
class Event:
    name: str


class EventsQueue:

    _instance: "EventsQueue"
    _queue: Queue[Event]

    def __new__(cls, *args, **kwargs) -> "EventsQueue":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._queue = Queue()
        return cls._instance

    @property
    def queue(self) -> Queue[Event]:
        return self._queue


def get_events_queue() -> Queue[Event]:
    return EventsQueue().queue


def emit_event(name: str) -> None:
    event = Event(name=EventTypes[name].value)
    queue = get_events_queue()
    queue.put_nowait(item=event)
