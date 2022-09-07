from asyncio import to_thread


async def as_async(sync_callable):
    return await to_thread(sync_callable)
