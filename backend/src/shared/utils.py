from asyncio import to_thread


async def as_async(sync_callable):
    """
    This function is a simple wrapper to the asyncio.to_thread function. It takes a synchronous function and runs it in a separated thread
    where the GIL will be unlocked whenever an IO operation happens.

    Usage:

        await as_async(lambda: some_synchronous_function(myArg1, myArg2, ..., myArgN))
    """

    return await to_thread(sync_callable)
