from asyncio import all_tasks, get_running_loop, to_thread
from decimal import Decimal, getcontext
from time import time
from typing import Callable, Coroutine


async def as_async(sync_callable: Callable):
    """
    This function is a simple wrapper to the asyncio.to_thread function. It takes a synchronous function and runs it in a separated thread
    where the GIL will be unlocked whenever an IO operation happens.

    Usage:

        await as_async(lambda: some_synchronous_function(myArg1, myArg2, ..., myArgN))
    """

    return await to_thread(sync_callable)


def async_timer(*, precision_level: int = 2):
    """
    This function works as a decorator for coroutines in order to capture their execution time and log it to the log's handlers
    """
    from .logging.logger import AsyncLogger

    def _async_timer(coroutine: Coroutine, /):
        async def decorator(*args, **kwargs):

            # Setting the precision level from the decimal class
            getcontext().prec = precision_level

            start = Decimal(time())

            logger: AsyncLogger = kwargs["logger"]
            coroutine_return = await coroutine(*args, **kwargs)

            end = Decimal(time())
            total = end - start

            await logger.log(f"Took {total} seconds to run the {coroutine.__name__} coroutine", level="DEBUG")

            return coroutine_return

        return decorator

    return _async_timer


def sync_timer(*, precision_level: int = 2):
    """
    This function works as a decorator for functions in order to capture their execution time and log it to the log's handlers
    """

    from .logging.logger import SyncLogger

    def _sync_timer(function: Callable, /):
        def decorator(*args, **kwargs):

            # Setting the precision level from the decimal class
            getcontext().prec = precision_level

            start = Decimal(time())

            logger: SyncLogger = kwargs["logger"]
            function_return = function(*args, **kwargs)

            end = Decimal(time())
            total = end - start

            logger.log(f"Took {total} seconds to run the {function.__name__} coroutine", level="DEBUG")

            return function_return

        return decorator

    return _sync_timer


def graceful_shutdown(coroutine: Coroutine):

    # TODO: Implement the functionality to await all pending tasks and then finish the execution of the program. Check Lynn's Root video

    async def decorator(*args, **kwargs):
        try:
            return await coroutine(*args, **kwargs)
        except Exception as err:
            print("An error ocurred. Cancelling all pending tasks from within loop. Error: %s" % err)
            for task in all_tasks():
                task.cancel()
        finally:
            loop = get_running_loop()
            loop.close()

    return decorator
