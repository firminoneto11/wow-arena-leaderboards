from asyncio import Queue, AbstractEventLoop

from .event import Event


class EventLoop(AbstractEventLoop):
    events_queue: Queue[Event]

    def register_event(self, item: Event) -> None:
        ...
