from asyncio import to_thread
from typing import Callable


async def to_async(sync_callable: Callable, /, *args, **kwargs):
    """
    This function is a simple wrapper to the asyncio.to_thread function. It takes a synchronous function and it's arguments and runs it in a separated thread where the GIL will be unlocked whenever an IO operation happens.

    Usage:

        await to_async(some_synchronous_function, myArg1, myArg2, ..., myArgN)

    """

    return await to_thread(sync_callable, *args, **kwargs)
