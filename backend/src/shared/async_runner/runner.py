from asyncio import all_tasks, current_task, get_event_loop, gather, AbstractEventLoop
from typing import Final
from asyncio.events import set_event_loop
from signal import Signals
from platform import system
import signal as signal_module

from decouple import config as get_env_var

from ..logging import Logger
from .events import get_events_queue
from .types import _Coroutine


class Runner:

    event_loop: AbstractEventLoop
    main_coroutine: type[_Coroutine]
    logger: Logger
    CUR_OS: Final[str] = system().upper()
    WINDOWS: Final[str] = "WINDOWS"
    IS_DEV: Final[bool] = get_env_var("IS_DEV", default=True, cast=bool)
    should_log: bool = True

    def __init__(self, main_coroutine: type[_Coroutine]) -> None:
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
                coroutine = self.shutdown()
                self.event_loop.run_until_complete(coroutine)
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

    def create_loop(self) -> None:
        """This method creates a new event loop and set some configurations in it"""

        def exception_handler(self, context: dict) -> None:

            # context["message"] will always be there, but context["exception"] may not
            msg = context.get("exception", context["message"])

            if self.should_log:
                self.logger.sCritical(f"Unhandled exception during 'run_main()' shutdown:")
                self.logger.sCritical(msg)

            self.event_loop.create_task(self.shutdown(by_exception=True))

        self.event_loop = get_event_loop()

        # Setting the event's loop debug level
        if self.IS_DEV:
            return self.event_loop.set_debug(enabled=True)

        # Setting the event's loop global exception handler (Avoiding massive crashes on production)
        # self.event_loop.set_exception_handler(handler=exception_handler)

    def set_signal_handlers(self) -> None:

        # TODO: Test in Linux environments

        def _signal_callback(sig: Signals):
            coroutine = self.shutdown(signal=sig)
            return self.event_loop.run_until_complete(coroutine)

        SHUTDOWN_SIGNALS: Final[tuple[Signals]] = (signal_module.SIGTERM, signal_module.SIGINT)

        # Adding a signal handler for each signal
        for signal in SHUTDOWN_SIGNALS:
            self.event_loop.add_signal_handler(
                sig=signal,
                callback=_signal_callback
                # callback=lambda sig=signal: self.event_loop.run_until_complete(self.shutdown(signal=sig)),
            )

    def start_loop(self) -> None:
        """
        Creating a task and running the loop forever. This way, the default exception handler will always be called, in case of
        exceptions. If we were using 'run_until_complete', any exceptions raised inside the event loop would be propagated to the main
        thread in the sync context.
        """
        self.event_loop.create_task(self.listen_for_events())
        self.event_loop.create_task(self.main_coroutine)
        self.event_loop.run_forever()

    def close_loop(self) -> None:
        self.event_loop.close()
        set_event_loop(loop=None)

        if self.should_log:
            self.logger.sInfo("Successfully shutdown the service.")

    async def shutdown(self, signal: Signals | None = None, by_exception: bool = False) -> None:
        """Method that should be used in order to shutdown the event loop."""

        async def finish_loop(loop: AbstractEventLoop) -> None:
            """Simply stops a event loop and cleans it up."""

            # Closing async generators and the default ThreadPoolExecutor
            await loop.shutdown_asyncgens()
            await loop.shutdown_default_executor()

            # Stopping the event loop
            loop.stop()

        msg = "Gathering tasks to cancel and shutting down..."

        if not by_exception:
            msg = f"Received exit signal: {signal.name if signal is not None else 'SIGINT'}. " + msg

        if self.should_log:
            await self.logger.info(msg)

        # Collecting the remaining tasks
        remaining_tasks = [t for t in all_tasks(loop=self.event_loop) if t is not current_task(self.event_loop)]

        if not remaining_tasks:
            return await finish_loop(loop=self.event_loop)

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

        return await finish_loop(loop=self.event_loop)

    async def listen_for_events(self) -> None:
        queue = get_events_queue()
        while True:
            item = await queue.get()
            if item.name == "cli-shutdown":
                self.should_log = False
                return await self.shutdown()
