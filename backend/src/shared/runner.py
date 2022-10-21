from asyncio import all_tasks, current_task, get_event_loop, AbstractEventLoop, gather, Queue
from asyncio.events import set_event_loop
from typing import Coroutine, Final
from dataclasses import dataclass
import signal as signals_module
from signal import Signals
from platform import system

from decouple import config as get_env_var

from .logging import Logger


@dataclass
class Event:
    name: str


class EventLoop(AbstractEventLoop):
    events_queue: Queue[Event]

    def register_event(self, item: Event) -> None:
        ...


class Runner:

    main_coroutine: Coroutine
    logger: Logger
    event_loop: EventLoop
    CUR_OS: Final[str] = system().upper()
    WINDOWS: Final[str] = "WINDOWS"
    IS_DEV: Final[bool] = get_env_var("IS_DEV", default=True, cast=bool)
    should_log: bool = True

    def __init__(self, main_coroutine: Coroutine) -> None:
        self.main_coroutine = main_coroutine
        self.logger = Logger(name="Event Loop logs")

    def __call__(self) -> None:

        # Creating an event loop
        self.create_loop()

        # Checking if the current OS is a windows machine and then running it
        if self.CUR_OS == self.WINDOWS:
            try:
                self.start_loop()
            except KeyboardInterrupt:
                self.event_loop.run_until_complete(self.shutdown_handler())
            finally:
                self.close_loop()
            return

        # Adding signal handlers
        self.set_signal_handlers()

        # Running it
        try:
            self.start_loop()
        finally:
            self.close_loop()

    def set_loop_configs(self) -> None:

        # Setting the event's loop debug level
        if self.IS_DEV:
            return self.event_loop.set_debug(enabled=True)

        # Setting the event's loop global exception handler (Avoiding massive crashes on production)
        self.event_loop.set_exception_handler(handler=self.exception_handler)

    def set_signal_handlers(self) -> None:

        # TODO: Test in Linux environments

        def _signal_callback(sig: Signals):
            return self.event_loop.run_until_complete(self.shutdown_handler(signal=sig))

        # Collecting the signals that will be used
        SHUTDOWN_SIGNALS: Final[tuple[Signals]] = (signals_module.SIGTERM, signals_module.SIGINT)

        # Adding a signal handler for each signal
        for signal in SHUTDOWN_SIGNALS:
            self.event_loop.add_signal_handler(
                sig=signal,
                callback=_signal_callback
                # callback=lambda sig=signal: self.event_loop.run_until_complete(self.shutdown_handler(signal=sig)),
            )

    def patch_event_loop(self) -> None:
        """This method patches the event loop in a way so it can satisfy the props defined in the EventLoop class."""

        def register_event(item: Event) -> None:
            self.event_loop.events_queue.put_nowait(item=item)

        # Patching the loop to have the attributes defined in 'EventLoop' class
        self.event_loop.events_queue = Queue()
        self.event_loop.register_event = register_event

    async def listen_for_events(self) -> None:
        while True:
            item = await self.event_loop.events_queue.get()
            if item.name == "cli-shutdown":
                self.should_log = False
                return await self.shutdown_handler()

    def create_loop(self) -> None:
        """
        This method creates a new event loop and adds some attributes over it, in order to react to events that might happen.
        """

        # Creating a new event loop and setting some configs
        self.event_loop = get_event_loop()
        self.set_loop_configs()
        self.patch_event_loop()

    def start_loop(self) -> None:
        """
        Creating a task and running the loop forever. This way, the default exception handler will always be called, in case of
        exceptions. If we were using 'run_until_complete', the loop would be closed because this method raises the exception that the
        coroutine raised without the default exception handler being called.
        """
        self.event_loop.create_task(self.listen_for_events())
        self.event_loop.create_task(self.main_coroutine())
        self.event_loop.run_forever()

    def close_loop(self) -> None:
        self.event_loop.close()
        set_event_loop(loop=None)

        if self.should_log:
            self.logger.sInfo("Successfully shutdown the service.")

    def exception_handler(self, context: dict) -> None:

        # context["message"] will always be there, but context["exception"] may not
        msg = context.get("exception", context["message"])

        if self.should_log:
            self.logger.sCritical(f"Unhandled exception during 'run_main()' shutdown:")
            self.logger.sCritical(msg)

        self.event_loop.create_task(self.shutdown_handler(by_exception=True))

    async def finish_loop(self) -> None:
        """
        Simply stops the event loop and cleans it up.

        Cleaning up loop - Cleaning up has to be executed from within the signal handler, because the signal could be triggered from
        anywhere outside the exception handling, which could lead to another exception.
        """

        # Closing async generators
        await self.event_loop.shutdown_asyncgens()

        # Closing the default ThreadPoolExecutor
        await self.event_loop.shutdown_default_executor()

        # Stopping the event loop
        self.event_loop.stop()

    async def shutdown_handler(
        self,
        signal: Signals | None = None,
        by_exception: bool = False,
    ) -> None:

        msg = "Gathering tasks to cancel and shutting down..."

        if not by_exception:
            msg = f"Received exit signal: {signal.name if signal is not None else 'SIGINT'}. " + msg

        if self.should_log:
            await self.logger.info(msg)

        # Collecting the remaining tasks
        remaining_tasks = [t for t in all_tasks(loop=self.event_loop) if t is not current_task(self.event_loop)]

        if not remaining_tasks:
            return await self.finish_loop()

        if self.should_log:
            await self.logger.info(f"Cancelling {len(remaining_tasks)} tasks.")

        # Cancelling them
        for task in remaining_tasks:
            task.cancel()

        # -- Finishing the remaining tasks --
        # If 'return_exceptions' is True, exceptions in the tasks are treated the same as successful results, and gathered in the result
        # list; otherwise, the first raised exception will be immediately propagated to the returned future.
        await gather(*remaining_tasks, return_exceptions=True)

        # Checking if the task had any exceptions and calling the exception handler if they did
        for task in remaining_tasks:
            if task.cancelled():
                continue
            if task.exception() is not None:
                self.event_loop.call_exception_handler(
                    {
                        "message": "unhandled exception during asyncio.run() shutdown",
                        "exception": task.exception(),
                        "task": task,
                    }
                )

        return await self.finish_loop()


def run_coroutine(coroutine: Coroutine) -> None:
    runner = Runner(main_coroutine=coroutine)
    return runner()