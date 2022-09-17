from asyncio import all_tasks, get_event_loop, AbstractEventLoop, gather
from asyncio.events import set_event_loop
from typing import Callable, Coroutine, Final
from platform import system
import signal

from shared import SyncLogger


def shutdown_handler(*, loop: AbstractEventLoop, logger: SyncLogger, signal: signal.Signals = None) -> None:

    if signal is not None:
        logger.log(f"Received exit signal: {signal.name}. Gathering tasks to cancel")

    # Collecting the remaining tasks
    remaining_tasks = all_tasks(loop=loop)

    if not remaining_tasks:
        return

    logger.log(f"Cancelling {len(remaining_tasks)} tasks")

    # Cancelling them
    for task in remaining_tasks:
        task.cancel()

    # Finishing the remaining tasks
    loop.run_until_complete(future=gather(*remaining_tasks, return_exceptions=True))

    # Checking if the task had any exceptions and calling the exception handler if they did
    for task in remaining_tasks:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "unhandled exception during asyncio.run() shutdown",
                    "exception": task.exception(),
                    "task": task,
                }
            )


def run_main_coroutine(async_function: Callable[..., Coroutine], debug: bool | None = None) -> None:

    CUR_OS: Final[str] = system().upper()

    # Creating a sync logger for this function
    logger = SyncLogger(name="Event Loop logs")

    # Creating a new event loop
    event_loop = get_event_loop()

    # Setting the event's loop debug level
    if debug is not None:
        event_loop.set_debug(enabled=debug)

    # Adding a signal handler for each signal (Only for non Windows platforms)
    if CUR_OS != "WINDOWS":

        # TODO: Test in Linux environments

        # Collecting the signals that will be used
        SHUTDOWN_SIGNALS: Final[tuple[signal.Signals]] = (signal.SIGTERM, signal.SIGINT)

        for _signal in SHUTDOWN_SIGNALS:
            event_loop.add_signal_handler(
                sig=_signal,
                callback=lambda sig=_signal: shutdown_handler(signal=sig, loop=event_loop, logger=logger),
            )

    try:
        event_loop.run_until_complete(future=async_function())
    except KeyboardInterrupt:
        if CUR_OS == "WINDOWS":
            shutdown_handler(loop=event_loop, logger=logger)
    finally:
        # Cleaning up loop
        event_loop.run_until_complete(future=event_loop.shutdown_asyncgens())
        event_loop.run_until_complete(future=event_loop.shutdown_default_executor())

        # Stopping the event loop, closing it and setting the thread's event loop to None
        set_event_loop(loop=None)
        event_loop.stop()
        event_loop.close()

    logger.log("Shutdown complete")
