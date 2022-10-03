from asyncio import sleep, create_task
from typing import Coroutine
from functools import wraps

from db_populator.exceptions import CouldNotFetchError
from db_populator.constants import DELAY
from ..exceptions import CouldNotExecuteError

# TODO: Check if the coroutine has to be re created, because it was awaited already
# TODO: An Exception should be raised when the 'number_of_tries' is not enough to execute the coroutine
# TODO: Use regular profiling instead of timing decorators


def re_try(number_of_tries: int, /):

    SPAN_COROUTINE_NAMES = ["fetch"]

    def _re_try(coroutine: Coroutine, /):
        @wraps(coroutine)
        async def decorator(*args, **kwargs):

            from db_populator import get_global_logger

            logger = get_global_logger()
            latest_exception = None
            coroutine_name = coroutine.__name__

            for n in range(number_of_tries):
                cur = n + 1
                try:
                    if coroutine_name not in SPAN_COROUTINE_NAMES:
                        create_task(
                            logger.info(
                                f"Executing the '{coroutine_name}' coroutine. {cur} out of {number_of_tries} tries."
                            )
                        )
                    return await coroutine(*args, **kwargs)
                except CouldNotFetchError as err:

                    latest_exception = err

                    create_task(
                        logger.error(
                            f"The following exception occurred while trying to execute the '{coroutine_name}' coroutine."
                        )
                    )

                    create_task(logger.error(latest_exception))

                    if cur != number_of_tries:
                        create_task(logger.warning(f"Retrying in {DELAY} seconds."))
                        await sleep(DELAY)

            create_task(
                logger.warning(f"Could not execute the '{coroutine_name}' coroutine after {number_of_tries} tries.")
            )

            raise CouldNotExecuteError from latest_exception

        return decorator

    return _re_try
