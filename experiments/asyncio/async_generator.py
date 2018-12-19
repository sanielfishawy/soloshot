import asyncio

async def async_num_gen():
    for num in range(3):
        yield num

def sync_num_gen():
    for num in range(3):
        yield num

async def async_get_all_nums():
    print('async nums')
    aiter = async_num_gen()
    async for num in aiter:
        print(num)

print('sync nums')
for i in sync_num_gen():
    print(i)

itr = sync_num_gen()
print("sync next", next(itr))
print("sync next", next(itr))
print("sync next", next(itr))

asyncio.run(async_get_all_nums())

aiter = async_num_gen()
print('async next', asyncio.run(aiter.__anext__()))
print('async next', asyncio.run(aiter.__anext__()))
print('async next', asyncio.run(aiter.__anext__()))

a = 1
