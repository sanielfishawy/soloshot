import sys
import os
import asyncio
from threading import Thread, Event
import logging

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
        self.connection_closed_event = Event()

        self._log = logging.getLogger(__class__.__name__)
        self._debug = logging.getLogger().getEffectiveLevel() == logging.DEBUG

    def open(self):
        self.start() # super Thread

    def run(self):
        asyncio.run(self._run_coro(), debug=self._debug)
        self.connection_open_event.set()
        self.connection_closed_event.wait()

    async def _run_coro(self):
        self._log.debug('Opening')
        reader, writer = await asyncio.open_connection(
            host=self._host_ip,
            port=self._port,
        )

        await self.send_and_receive_foo(writer, reader)
        await self.send_and_receive_foo(writer, reader)
        await self.close(writer)


    async def send_and_receive_foo(self, writer, reader):
        self._log.debug('Writing foo')
        writer.write('foo\n'.encode())
        await writer.drain()
        self._log.debug('Sent foo')
        self._log.debug('Waiting on readline')
        r = await reader.readline()
        self._log.debug('Received %s', r.decode())

    async def close(self, writer):
        self._log.debug('Writing eof')
        writer.write_eof()
        self._log.debug('Waiting writing eof')
        await writer.drain()
        self._log.debug('Closing')
        writer.close()
        self._log.debug('Waiting closing')
        await writer.wait_closed()
        self._log.debug('Closed')