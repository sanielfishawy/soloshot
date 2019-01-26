# pylint: disable=C0413
import sys
import os
import enum
import time
import logging

sys.path.insert(0, os.getcwd())
from remote_control.tcp_connection import TcpConnection
from remote_control.request_response_object import RequestResponseObject
import remote_control.base_commands as BC

class BaseState(enum.Enum):
    DISCONNECTED = enum.auto()
    CONNECTED = enum.auto()
    POWERED_ON = enum.auto()

class BaseController:

    def __init__(
            self,
            ip,
            port=8080,
        ):

        self._state = BaseState.DISCONNECTED

        self._tcp_connection = TcpConnection(ip, port)
        self._tcp_connection.open()
        self._tcp_connection.connection_open_event.wait()

    def connect(self):
        if self._state == BaseState.DISCONNECTED:
            self.send_request(BC.connect())
            self._state = BaseState.CONNECTED

    def power_on(self):
        self.connect()
        if self._state == BaseState.CONNECTED:
            self.send_request(BC.init())
            time.sleep(1)
            self.send_request(BC.boot_controllers())
            time.sleep(2)
            self.send_request(BC.enable_motors())
            time.sleep(2)
            self._state = BaseState.POWERED_ON

    def power_off(self):
        if self._state == BaseState.POWERED_ON:
            self.send_request(BC.deinit())
        self._state = BaseState.CONNECTED

    def pan_and_tilt_continously(self, pan_deg_per_sec, tilt_deg_per_sec=0):
        self.power_on()
        self.send_request(BC.pan_and_tilt_continously(pan_deg_per_sec, tilt_deg_per_sec))

    def send_request(
            self,
            request_response_object: RequestResponseObject,
    ):
        self._tcp_connection.queue_request(request_response_object)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(threadName)10s %(name)18s: %(message)s',
        stream=sys.stderr,
    )
    bc = BaseController('192.168.1.85')
    for i in range(7):
        bc.pan_and_tilt_continously(20*i)
        time.sleep(4)
        bc.pan_and_tilt_continously(-20*i)
        time.sleep(4)

    bc.pan_and_tilt_continously(0)
