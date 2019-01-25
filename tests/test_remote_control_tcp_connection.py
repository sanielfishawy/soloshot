# pylint: disable=C0413
import sys
import os
import unittest
import logging
from threading import Event

sys.path.insert(0, os.getcwd())
from remote_control.echo_server import EchoServer
from remote_control.tcp_connection import TcpConnection
from remote_control.request_response_object import RequestResponseObject


class TestRemoteControlTcpConnection(unittest.TestCase):

    BASE_IP = '192.168.1.85'
    BASE_PORT = 8080

    def setUp(self):

        logging.basicConfig(
            level=logging.INFO,
            format='%(threadName)10s %(name)18s: %(message)s',
            stream=sys.stderr,
        )

        self.log = logging.getLogger(__class__.__name__)

        self.server = EchoServer()
        self.server.start()
        self.server.started_event.wait()

        # self.tcp_connection_to_echo = TcpConnection(
        #     host_ip=self.server.host_ip,
        #     port=self.server.port,
        # )

        self.tcp_connection_to_base = TcpConnection(
            host_ip=self.__class__.BASE_IP,
            port=self.__class__.BASE_PORT,
        )
        self.tcp_connection_to_base.open()
        self.tcp_connection_to_base.connection_open_event.wait()

    def test_send_requests(self):
        requests = [
            RequestResponseObject(
                request=f'#CONNECT\n',
                callback=self.callback,
            ),
            RequestResponseObject(
                request=f'#INIT\n',
                callback=self.callback,
            ),
        ]
        for rro in requests:
            self.tcp_connection_to_base.queue_request(rro)

    def callback(self, rro: RequestResponseObject):
        self.log.debug('request: %s', rro.request)
        self.log.debug('response: %s', rro.response)

if __name__ == '__main__':
    unittest.main()
