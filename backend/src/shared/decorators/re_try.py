from typing import Coroutine
from functools import wraps
from asyncio import sleep

from db_populator.constants import DELAY


# TODO: Check if the coroutine has to be re created, because it was awaited already
# TODO: An Exception should be raised when the 'number_of_tries' is not enough to execute the coroutine
# TODO: Use regular profiling instead of timing decorators


def re_try(number_of_tries: int, /):

    from shared import Logger

    def _re_try(coroutine: Coroutine, /):
        @wraps(coroutine)
        async def decorator(*args, **kwargs):
            logger: Logger = kwargs["logger"]
            for n in range(number_of_tries):
                cur = n + 1
                try:
                    await logger.info(
                        f"Executing the '{coroutine.__name__}' coroutine. {cur} out of {number_of_tries} tries."
                    )
                    return await coroutine(*args, **kwargs)
                except Exception as err:

                    message = f"The following exception occurred while trying to execute the '{coroutine.__name__}' coroutine."

                    if cur != number_of_tries:
                        message += f" Retrying in {DELAY} seconds."

                    await logger.error(message)
                    await logger.error(err)
                    await sleep(DELAY)

            await logger.warning(
                f"Could not execute the '{coroutine.__name__}' coroutine after {number_of_tries} tries."
            )

        return decorator

    return _re_try
