from multiprocessing import Process
from asyncio import sleep, get_running_loop, run as run_in_event_loop
from settings import UPDATE_EVERY
from typing import Awaitable


class AsyncProcess(Process):

    async def target_handler(self, target: Awaitable):
        while True:
            await sleep(UPDATE_EVERY)
            await target(*self._args, **self._kwargs)

    def run(self):
        if self._target:
            try:
                run_in_event_loop(self.target_handler(target=self._target))
            except KeyboardInterrupt:
                pass
            except Exception as e:
                print(f"Error while closing the event loop: {e}")

    def terminate(self):
        try:
            loop = get_running_loop()
            loop.stop()
            loop.close()
        except RuntimeError:
            print("No event loop running.")
        finally:
            super().terminate()


def start_sub_process(task: Awaitable) -> AsyncProcess:
    sub_process = AsyncProcess(target=task)
    sub_process.start()
    return sub_process
