from typing import Coroutine
from asyncio import sleep

from db_populator.constants import DELAY
from shared import AsyncLogger


# TODO: Check if the coroutine has to be re created, because it was awaited already


def re_try(number_of_tries: int, /):
    def _re_try(coroutine: Coroutine, /):
        async def decorator(*args, **kwargs):
            logger: AsyncLogger = kwargs["logger"]
            for _ in range(number_of_tries):
                try:
                    return await coroutine(*args, **kwargs)
                except Exception as err:
                    message = (
                        f"The following exception occurred while trying to execute the '{coroutine.__name__}' coroutine. "
                        f"Retrying in {DELAY} seconds."
                    )
                    await logger.error(message)
                    await logger.error(err)
                    # await sleep(DELAY)
                    await sleep(1)
            await logger.warning(
                f"Could not execute the '{coroutine.__name__}' coroutine after {number_of_tries} tries"
            )

        return decorator

    return _re_try
