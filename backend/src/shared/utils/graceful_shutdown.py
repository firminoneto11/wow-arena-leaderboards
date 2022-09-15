from typing import Coroutine
from asyncio import all_tasks, get_running_loop


def graceful_shutdown(coroutine: Coroutine):

    # TODO: Implement the functionality to await all pending tasks and then finish the execution of the program. Check Lynn's Root video

    async def decorator(*args, **kwargs):
        try:
            return await coroutine(*args, **kwargs)
        except Exception as err:
            print("An error ocurred. Cancelling all pending tasks from within loop. Error: %s" % err)
            for task in all_tasks():
                task.cancel()
        finally:
            loop = get_running_loop()
            loop.close()

    return decorator
