import sys
import os
import unittest
import logging
import asyncio

sys.path.insert(0, os.getcwd())
from remote_control.echo_server import EchoServer
from remote_control.tcp_connection import TcpConnection


class TestRemoteControlTcpConnection(unittest.TestCase):

    def setUp(self):

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(threadName)10s %(name)18s: %(message)s',
            stream=sys.stderr,
        )

        self.log = logging.getLogger(__class__.__name__)

        self.server = EchoServer()
        self.server.start()
        self.server.started_event.wait()

        self.tcp_connection = TcpConnection(
            host_ip=self.server.host_ip,
            port=self.server.port,
        )

    def tearDown(self):
        self.server.stop()

    def test_open_close(self):
        self.tcp_connection.open()
        self.tcp_connection.connection_open_event.wait()



if __name__ == '__main__':
    unittest.main()