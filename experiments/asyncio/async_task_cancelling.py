import asyncio
from threading import Thread, Event
import time
import concurrent.futures

class Worker(Thread):

    def __init__(self):
        super().__init__()
        self._task = None

    def stop(self):
        self._task.cancel()

    async def worker(self):
        for i in range(1000):
            print(i)
            await asyncio.sleep(1)

    async def run_worker(self):
        self._task = asyncio.create_task(self.worker())
        await self._task

    def run(self):
        try:
            asyncio.run(self.run_worker())
        except asyncio.CancelledError:
            print('self._task.cancelled():', self._task.cancelled())



worker = Worker()
worker.start()
time.sleep(5)
worker.stop()