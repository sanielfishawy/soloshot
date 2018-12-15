import asyncio

async def say_after(msg, delay):
    print(f'Starting {msg}')
    await asyncio.sleep(delay)
    print(f'Finished {msg}')
    return f'{msg}:  {str(delay)}'

async def main():
    task_1 = asyncio.create_task(
        say_after('task_1', 5)
    )
    task_2 = asyncio.create_task(
        say_after('task_2', 10)
    )
    task_3 = asyncio.create_task(
        say_after('task_3', 15)
    )

    result = await asyncio.gather(
        task_1,
        task_2,
        task_3,
    )

    print(result)

asyncio.run(main())
