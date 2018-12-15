import sys
import os
import asyncio

sys.path.insert(0, os.getcwd())

class TcpConnection():
    '''
    Opens a tcp connection at domain_ip and port. Provides a reader and writer
    '''

    def __init__(
            self,
            host_ip: str,
            port: int,
    ):
        self._host_ip = host_ip
        self._port = port

        # lazy init
        self._writer = None
        self._reader = None

    def get_reader(self) -> asyncio.StreamReader:
        if self._reader is None:
            asyncio.get_event_loop().run_until_complete(
                self._open_connection()
            )
        return self._reader

    def get_writer(self) -> asyncio.StreamWriter:
        if self._writer is None:
            asyncio.get_event_loop().run_until_complete(
                self._open_connection()
            )
        return self._writer

    def close_connection(self):
        asyncio.get_event_loop().run_until_complete(self._close_connection())

    async def _close_connection(self):
        if self._writer is not None:
            self._writer.close()
            await self._writer.wait_closed()
        self._reader = None
        self._writer = None

    async def _open_connection(self):
        self._reader, self._writer = await asyncio.open_connection(
            host=self._host_ip,
            port=self._port,
        )
