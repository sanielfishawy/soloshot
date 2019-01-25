# pylint: disable=C0413
import sys
import os
import asyncio
from threading import Thread, Event
import logging

sys.path.insert(0, os.getcwd())

class EchoServer(Thread):
    '''
    A simple echo server for testing TCP connections on a new Thread.
    host_ip: 127.0.0.1
    port: 8888

    Server may not be restarted after stopped. Create a new instance if desired.
    '''

    def __init__(
            self,
    ):
        super().__init__()

        self.host_ip = '127.0.0.1'
        self.port = 8888
        self.started_event = Event()
        self.stopped_event = Event()

        self._server = None
        self._run_forever_task = None
        self._request_stop_event = Event()

        self._log = logging.getLogger(self.__class__.__name__)

    def is_serving(self):
        if self._server:
            return self._server.is_serving()
        return False

    def sockets(self):
        if self._server:
            return self._server.sockets()
        return []

    def stop(self):
        self._run_forever_task.cancel()

    def run(self):
        asyncio.run(self._start_server())
        # try:
        #     asyncio.run(self._start_server())
        # except asyncio.CancelledError:
        #     self.stopped_event.set()
        #     self._log.debug('Stopped')

    async def _start_server(self):
        self._server = await asyncio.start_server(
            client_connected_cb=self._handle_server_connection,
            host=self.host_ip,
            port=self.port,
            start_serving=False,
        )
        addr = self._server.sockets[0].getsockname()
        self._log.debug('Serving on %s', addr)
        self.started_event.set()

        self._run_forever_task = asyncio.create_task(self._server.serve_forever())
        await self._run_forever_task

        # async with self._server:
            # await self._server.serve_forever()

    async def _handle_server_connection(
            self,
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter,
    ):
        while True:
            # data = await reader.readline()
            data = await reader.read(10)
            message = data.decode()

            addr = writer.get_extra_info('peername')
            self._log.debug(
                'Received "%s" from %s',
                message,
                addr,
            )

            writer.write(data)
            await writer.drain()

            self._log.debug(
                'Sent "%s" to %s',
                message,
                addr,
            )