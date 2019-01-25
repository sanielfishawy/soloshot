# pylint: disable=C0413
import os
import sys
import unittest
import logging

sys.path.insert(0, os.getcwd())
from remote_control.tcp_connection import TcpConnection
from remote_control.echo_server import EchoServer

class TestRemoteControlEchoServer(unittest.TestCase):

    def setUp(self):
        # asyncio.set_event_loop_policy(EventLoopPolicy())
        self.server = EchoServer()
        self.client = TcpConnection(
            host_ip=self.server.host_ip,
            port=self.server.port,
        )

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(threadName)10s %(name)18s: %(message)s',
            stream=sys.stderr,
        )
        self.log = logging.getLogger(__class__.__name__)

    def test_start_stop_server(self):
        self.log.debug('Starting server')
        self.server.start()
        self.log.debug('Waiting on started event')
        self.server.started_event.wait()
        self.log.debug('Is serving = %s', self.server.is_serving())
        self.assertTrue(self.server.is_serving())
        self.log.debug('Stopping server')
        self.server.stop()
        self.log.debug('Is serving = %s', self.server.is_serving())
        self.log.debug('Waiting on stopped event')
        self.server.stopped_event.wait()
        self.log.debug('Got stopped event')


if __name__ == '__main__':
    unittest.main()
