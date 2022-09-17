from asyncio import all_tasks, current_task, get_event_loop, AbstractEventLoop, gather
from asyncio.events import set_event_loop
from typing import Callable, Coroutine, Final
from platform import system
import signal

from shared import SyncLogger


# Creating a sync logger
logger = SyncLogger(name="Event Loop logs")


def exception_handler(loop: AbstractEventLoop, context: dict) -> None:
    # context["message"] will always be there; but context["exception"] may not
    msg = context.get("exception", context["message"])
    logger.log(f"Caught exception: {msg}", level="error")
    loop.create_task(coro=shutdown_handler(loop=loop, by_exception=True))


async def shutdown_handler(
    *, loop: AbstractEventLoop, signal: signal.Signals = None, by_exception: bool = False
) -> None:
    async def finish_loop() -> None:
        """
        Simply stops the event loop and cleans up the loop.

        Cleaning up loop - Cleaning up has to be executed from within the signal handler, because the signal could be triggered from
        anywhere outside the exception handling, which could lead to another exception.
        """

        # Closing async generators
        await loop.shutdown_asyncgens()

        # Closing the default ThreadPoolExecutor
        await loop.shutdown_default_executor()

        # Stopping the event loop
        loop.stop()

    msg = "Gathering tasks to cancel and shutting down..."

    if not by_exception:
        msg = f"Received exit signal: {signal.name if signal is not None else 'SIGINT'}. " + msg

    logger.log(msg)

    # Collecting the remaining tasks
    remaining_tasks = [t for t in all_tasks(loop=loop) if t is not current_task()]

    if not remaining_tasks:
        await finish_loop()
        return

    logger.log(f"Cancelling {len(remaining_tasks)} tasks")

    # Cancelling them
    for task in remaining_tasks:
        task.cancel()

    # -- Finishing the remaining tasks --
    # If 'return_exceptions' is True, exceptions in the tasks are treated the same as successful results, and gathered in the result list;
    # otherwise, the first raised exception will be immediately propagated to the returned future.
    await gather(*remaining_tasks, return_exceptions=True)

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

    await finish_loop()


def run_main_coroutine(async_function: Callable[..., Coroutine], debug: bool | None = None) -> None:

    CUR_OS: Final[str] = system().upper()

    # Creating a new event loop
    event_loop = get_event_loop()

    # Setting the event's loop global exception handler
    event_loop.set_exception_handler(handler=exception_handler)

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
                callback=lambda sig=_signal: event_loop.run_until_complete(
                    future=shutdown_handler(signal=sig, loop=event_loop)
                ),
            )

    if CUR_OS == "WINDOWS":
        try:
            # Creating a task and running the loop forever. This way, the default exception handler will always be called, in case of
            # exceptions. If we were using 'run_until_complete', the loop would be closed because this method raises the exception that the
            # coroutine raised without the default exception handler being called.
            event_loop.create_task(coro=async_function())
            event_loop.run_forever()
        except KeyboardInterrupt:
            if CUR_OS == "WINDOWS":
                event_loop.run_until_complete(future=shutdown_handler(loop=event_loop))
        finally:
            set_event_loop(loop=None)
            event_loop.close()
            logger.log("Successfully shutdown the service.")
    else:
        try:
            # Creating a task and running the loop forever. This way, the default exception handler will always be called, in case of
            # exceptions. If we were using 'run_until_complete', the loop would be closed because this method raises the exception that the
            # coroutine raised without the default exception handler being called.
            event_loop.create_task(coro=async_function())
            event_loop.run_forever()
        finally:
            set_event_loop(loop=None)
            event_loop.close()
            logger.log("Successfully shutdown the service.")
