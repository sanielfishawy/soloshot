import asyncio
import concurrent.futures
import time
import os
import threading

queue = asyncio.Queue()

def worker(name):
    print('in worker')


    while not queue.empty():
        got = queue.get_nowait()
        print(f'{name}: tid: {threading.get_ident()} got: {got})')
        time.sleep(1)
        queue.task_done()

async def main():

    for i in range(20):
        queue.put_nowait(i)

    loop = asyncio.get_running_loop()
    # for i in range(4):
        # print(f'adding worker {i}')
        # asyncio.create_task(worker(f'worker-{i}', queue))

    with concurrent.futures.ThreadPoolExecutor() as pool:
        workers = [
            loop.run_in_executor(pool, worker, f'worker-{i}')
            for i in range(20)
        ]
    await asyncio.gather(*workers)



asyncio.run(main())
