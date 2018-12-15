import asyncio

def do_something_that_takes_time():
    print('before run something')
    asyncio.run(something())
    print('after run something')
    asyncio.run(something())
    print('after second run')


async def something():
    await asyncio.sleep(1)
    print("done waiting")


do_something_that_takes_time()
