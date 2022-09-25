from decimal import Decimal, getcontext
from typing import Coroutine
from functools import wraps
from time import time


def async_timer(precision_level: int, /):
    """
    This function works as a decorator for coroutines in order to capture their execution time and log it to the log's handlers
    """
    from shared import Logger

    def _async_timer(coroutine: Coroutine, /):
        @wraps(coroutine)
        async def decorator(*args, **kwargs):

            # Setting the precision level from the decimal class
            getcontext().prec = precision_level

            start = Decimal(time())

            logger: Logger = kwargs["logger"]
            coroutine_return = await coroutine(*args, **kwargs)

            end = Decimal(time())
            total = end - start

            await logger.debug(f"Took {total} seconds to run the '{coroutine.__name__}' coroutine")

            return coroutine_return

        return decorator

    return _async_timer
