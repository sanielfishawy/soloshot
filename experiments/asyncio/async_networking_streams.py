import os
import sys
import asyncio

sys.path.insert(0, os.getcwd())

global reader, writer
reader = None
writer = None

async def tcp_echo_client(message, delay):
    global reader, writer
    await asyncio.sleep(delay)

    if reader is None:
        reader, writer = await asyncio.open_connection(
            host='127.0.0.1',
            port=8886,
        )

    print(f'Tcp_echo_client: Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    print(f'Tcp_echo_client: received: {data.decode()!r}')

    # writer.close()
    # await writer.wait_closed()

async def handle_server_cb(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Handle Echo: Received {message!r} from {addr!r}")
    writer.write(data)
    print(f"Handle Echo: Echoed back {message!r} to {addr!r}")
    # writer.close()

async def start_server():
    server = await asyncio.start_server(
        handle_server_cb, '127.0.0.1', 8886)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


async def get_std_in():
    while True:
        await asyncio.sleep(1)
        entry = sys.stdin.readline()
        if entry.strip() == 'q':
            print('Exiting get_std_in')
            loop = asyncio.get_running_loop()
            loop.shutdown_asyncgens()
            loop.stop()
            loop.close()
        yield entry

async def handle_keyboard_entry():
    async for entry in get_std_in():
        await tcp_echo_client(entry, 0.5)

async def main():

    await asyncio.gather(
        start_server(),
        handle_keyboard_entry(),
        # tcp_echo_client('foo bar1', 2),
        # tcp_echo_client('foo bar2', 3),
        return_exceptions=False,
    )

asyncio.run(main(), debug=False)