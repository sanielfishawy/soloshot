# pylint: disable=C0413
import os
import sys
import unittest
import asyncio

sys.path.insert(0, os.getcwd())
from remote_control.tcp_connection import TcpConnection
from remote_control.echo_server import EchoServer
from remote_control.event_loop_policy import EventLoopPolicy

class TestRemoteControlTcpConnection(unittest.TestCase):

    def setUp(self):
        # asyncio.set_event_loop_policy(EventLoopPolicy())
        self.server = EchoServer()
        self.server.start_server()
        self.client = TcpConnection(
            host_ip=self.server.host_ip,
            port=self.server.port,
        )

        self.reader = self.client.get_reader()
        self.writer = self.client.get_writer()

    def test_echo(self):
        asyncio.run(self.write('foo'), debug=True)

    async def write(self, message):
        self.writer.write(message.encode())
        data = await self.reader.read(100)
        print(data.decode())

if __name__ == '__main__':
    unittest.main()