from decimal import Decimal, getcontext
from typing import Callable
from time import time


def sync_timer(precision_level: int, /):
    """
    This function works as a decorator for functions in order to capture their execution time and log it to the log's handlers
    """

    from shared import Logger

    def _sync_timer(function: Callable, /):
        def decorator(*args, **kwargs):

            # Setting the precision level from the decimal class
            getcontext().prec = precision_level

            start = Decimal(time())

            logger: Logger = kwargs["logger"]
            function_return = function(*args, **kwargs)

            end = Decimal(time())
            total = end - start

            logger.sDebug(f"Took {total} seconds to run the '{function.__name__}' function")

            return function_return

        return decorator

    return _sync_timer
