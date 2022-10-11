from asyncio import all_tasks, current_task, get_event_loop, AbstractEventLoop, gather
from asyncio.events import set_event_loop
from typing import Coroutine, Final
from platform import system
from signal import Signals
import signal

from decouple import config as get_env_var

from shared import Logger


class Runner:

    main_coroutine: Coroutine
    logger: Logger
    event_loop: AbstractEventLoop
    CUR_OS: Final[str] = system().upper()
    WINDOWS: Final[str] = "WINDOWS"

    def __init__(self, main_coroutine: Coroutine) -> None:
        self.main_coroutine = main_coroutine
        self.logger = Logger(name="Event Loop logs")

    def start_loop(self) -> None:
        """
        Creating a task and running the loop forever. This way, the default exception handler will always be called, in case of
        exceptions. If we were using 'run_until_complete', the loop would be closed because this method raises the exception that the
        coroutine raised without the default exception handler being called.
        """
        self.event_loop.create_task(self.main_coroutine())
        self.event_loop.run_forever()

    def close_loop(self) -> None:
        self.event_loop.close()
        set_event_loop(loop=None)
        self.logger.sInfo("Successfully shutdown the service.")

    def exception_handler(self, context: dict) -> None:

        # context["message"] will always be there, but context["exception"] may not
        msg = context.get("exception", context["message"])

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

    async def shutdown_handler(self, signal: Signals | None = None, by_exception: bool = False) -> None:

        msg = "Gathering tasks to cancel and shutting down..."

        if not by_exception:
            msg = f"Received exit signal: {signal.name if signal is not None else 'SIGINT'}. " + msg

        await self.logger.info(msg)

        # Collecting the remaining tasks
        remaining_tasks = [t for t in all_tasks(loop=self.event_loop) if t is not current_task()]

        if not remaining_tasks:
            return await self.finish_loop()

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

    def __call__(self) -> None:

        # Creating a new event loop
        self.event_loop = get_event_loop()

        IS_DEV: bool = get_env_var("IS_DEV", default=True, cast=bool)
        if IS_DEV:
            # Setting the event's loop debug level
            self.event_loop.set_debug(enabled=True)
        else:
            # Setting the event's loop global exception handler (Avoiding massive crashes on production)
            self.event_loop.set_exception_handler(handler=self.exception_handler)

        # Adding a signal handler for each signal (Only for non Windows platforms)
        if self.CUR_OS != self.WINDOWS:

            # TODO: Test in Linux environments

            # Collecting the signals that will be used
            SHUTDOWN_SIGNALS: Final[tuple[Signals]] = (signal.SIGTERM, signal.SIGINT)

            for _signal in SHUTDOWN_SIGNALS:
                self.event_loop.add_signal_handler(
                    sig=_signal,
                    callback=lambda sig=_signal: self.event_loop.run_until_complete(self.shutdown_handler(signal=sig)),
                )

        if self.CUR_OS == self.WINDOWS:
            try:
                self.start_loop()
            except KeyboardInterrupt:
                self.event_loop.run_until_complete(self.shutdown_handler())
            finally:
                self.close_loop()
        else:
            try:
                self.start_loop()
            finally:
                self.close_loop()


def run_main(coroutine: Coroutine) -> None:
    runner = Runner(main_coroutine=coroutine)
    return runner()
