from typing import Coroutine

from shared import AsyncLogger


async def re_try(number_of_times: int, /):
    async def _re_try(coro: Coroutine):
        async def decorator(*args, **kwargs):
            logger: AsyncLogger = kwargs["logger"]
            for _ in range(number_of_times):
                try:
                    return await coro(*args, **kwargs)
                except:
                    logger.log(f"An error occurred while trying to execute the {coro.__name__} coroutine. Retrying")

        return decorator

    return _re_try
