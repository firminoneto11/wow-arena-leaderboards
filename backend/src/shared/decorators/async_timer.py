from decimal import Decimal, getcontext
from typing import Coroutine
from time import time


def async_timer(precision_level: int, /):
    """
    This function works as a decorator for coroutines in order to capture their execution time and log it to the log's handlers
    """
    from shared.logging import AsyncLogger

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
