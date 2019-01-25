import sys
import os
import asyncio
from threading import Thread, Event
import logging

sys.path.insert(0, os.getcwd())
from remote_control.request_response_object import RequestResponseObject

sys.path.insert(0, os.getcwd())

class TcpConnection(Thread):
    '''
    Opens a tcp connection at host_ip and port on a new Thread.
    To use:
        - start()
        - get_reader()
        - get_writer()
        - stop()

    Cannot be restarted use a new instance if desired.
    '''

    def __init__(
            self,
            host_ip: str,
            port: int,
    ):
        super().__init__()

        self._host_ip = host_ip
        self._port = port

        self.connection_open_event = Event()

        self._log = logging.getLogger(__class__.__name__)
        self._debug = logging.getLogger().getEffectiveLevel() == logging.DEBUG
        self._request_response_queue = None

    def queue_request(self, request_response_object: RequestResponseObject):
        self._request_response_queue.put_nowait(request_response_object)

    def open(self):
        self.start() # super Thread

    def run(self):
        # asyncio.run(self._run_coro(), debug=self._debug)
        asyncio.run(self._run_coro(), debug=True)

    async def _run_coro(self):
        self._log.info('Opening')

        self._request_response_queue = asyncio.Queue()

        reader, writer = await asyncio.open_connection(
            host=self._host_ip,
            port=self._port,
        )
        self.connection_open_event.set()

        await asyncio.gather(
            self._continuous_send_task(writer),
            self._continuous_receive_task(reader),
        )
        # while True:
        #     rro = self._request_response_queue.get()
        #     await self._send_request(rro.request, writer)
        #     rro.response = await self._get_response(reader)
        #     self._send_callback(rro)
        #     self._request_response_queue.task_done()

    def _send_callback(self, request_response_object: RequestResponseObject):
        if request_response_object.callback:
            request_response_object.callback(request_response_object)

    async def _continuous_send_task(self, writer):
        while True:
            rro = await self._request_response_queue.get()
            await self._send_request(rro.request, writer)
            self._log.info('sent: %s', rro.request)
            self._request_response_queue.task_done()

    async def _continuous_receive_task(self, reader):
        while True:
            response = await self._get_response(reader)
            self._log.info('recieved: %s', response)

    async def _send_request(self, request, writer):
        writer.write(request.encode())
        await writer.drain()

    async def _get_response(self, reader):
        r = await reader.readline()
        return r.decode()

    async def close(self, writer):
        writer.close()
        await writer.wait_closed()
        self._log.debug('Closed')