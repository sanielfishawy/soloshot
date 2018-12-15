# pylint: disable=C0413
import sys
import os
import asyncio

sys.path.insert(0, os.getcwd())

class EchoServer():
    '''
    A simple echo server for testing TCP connections.
    host_ip: 127.0.0.1
    port: 8888
    '''

    def __init__(
            self,
    ):
        self.host_ip = '127.0.0.1'
        self.port = 8888

        # lazy init
        self._server = None

        # asyncio.set_event_loop_policy(EventLoopPolicy())


    def start_server(self):
        asyncio.run(self._start_server())
        return self

    def stop_server(self):
        if self._server is not None:
            self._server.stop()
            self._server = None
        return self

    async def _start_server(self):
        if self._server is None:
            self._server = await asyncio.start_server(
                client_connected_cb=self._handle_server_connection,
                host=self.host_ip,
                port=self.port,
                start_serving=True,
            )
            addr = self._server.sockets[0].getsockname()
            print(f'Serving on {addr}')

    async def _handle_server_connection(
            self,
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter,
    ):
        data = await reader.read(100)
        message = data.decode()

        addr = writer.get_extra_info('peername')
        print(f"Handle Echo: Received {message!r} from {addr!r}")

        await writer.write(data)

        writer.close()
