import asyncio
import concurrent.futures
import time
import os

def show_pid(delay):
    print(f'show_pid: pid: {os.getpid()} delay: {delay}')
    time.sleep(delay)
    return os.getpid()

async def main():
    loop = asyncio.get_running_loop()
    with concurrent.futures.ProcessPoolExecutor() as pool:
        r1 = await loop.run_in_executor(pool, show_pid, 1)
        print(r1)

        result = await asyncio.gather(
            loop.run_in_executor(pool, show_pid, 1),
            loop.run_in_executor(pool, show_pid, 1),
            loop.run_in_executor(pool, show_pid, 1),
        )

    print(result)

asyncio.run(main())
