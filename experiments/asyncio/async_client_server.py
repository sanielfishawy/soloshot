import asyncio
import concurrent.futures

def start_client():
    pass

def server_cb(reader, writer):
    print('got server cb')


async def start_server():
    server = await asyncio.start_server(
        client_connected_cb=server_cb,
        host='127.0.0.1',
        port=8888,
    )

    print(f'Serving on {server.sockets[0].getsockname()}')
    await server.serve_forever()

async def sleepy():
    print('sleeping')
    await asyncio.sleep(2)
    print('awake')

async def kill_server(server_task):
    await asyncio.sleep(5)
    server_task.cancel()

async def main():
    start_server_task = asyncio.create_task(start_server())
    await asyncio.gather(
        start_server_task,
        sleepy(),
        kill_server(start_server_task),
        return_exceptions=True,
    )

async def main0():
    loop = asyncio.get_running_loop()
    with concurrent.futures.ProcessPoolExecutor() as pool:
        loop.run_in_executor(pool, main())

asyncio.run(main0())
print('server killed')
