# pylint: disable=C0413
import sys
import os
import unittest
import asyncio
import concurrent.futures

sys.path.insert(0, os.getcwd())
from remote_control.wifi_base_controller import BaseConnection, BaseController

class TestRemoteControlWifiBaseController(unittest.TestCase):

    def setUp(self):
        self.host_ip = '192.168.0.112'
        self.port = 8080

        self.base_connection = BaseConnection(
            host=self.host_ip,
            port=self.port,
            name='test_base_connection'
        )
        self.base_controller = BaseController(
            host=self.host_ip,
            port=self.port,
        )

        self.loop = asyncio.get_event_loop()

    def tearDown(self):
        self.loop.run_until_complete(self.disconnect())

    def dont_test_connect_and_disconnect(self):
        self.loop.run_until_complete(self.connect_and_disconnect())

    def test_send_k20_init(self):
        self.loop.run_until_complete(self.send_k20_init())

    def dont_test_move_motors(self):
        self.loop.run_until_complete(self.move_motors())

    async def send_k20_init(self):
        self.assertTrue(await self.base_controller.connect())

        loop = asyncio.get_running_loop()

        with concurrent.futures.ProcessPoolExecutor() as pool:
            await asyncio.gather(
                # loop.run_in_executor(pool, self.base_controller.run_requests),
                # loop.run_in_executor(pool, self.base_controller.send_k20_init),
                # asyncio.sleep(1),
                # asyncio.sleep(1),
            )
        await self.base_controller.send_k20_init()
        await self.base_controller.run_requests()
        await self.base_controller.run_requests()
        await self.base_controller.run_requests()

    async def move_motors(self):
        self.assertTrue(await self.base_controller.connect())
        await self.base_controller.run_requests()
        self.assertTrue(await self.base_controller.send_k20_init())
        com = "MOTOR,0,0,10,10"
        self.base_controller.request(com, confirmAck=False, confirmAction=False, motorRequest=True)
        self.assertTrue(await self.base_connection.disconnect())

    async def connect_and_disconnect(self):
        self.assertTrue(await self.base_connection.connect())
        self.assertTrue(await self.base_connection.disconnect())

    async def disconnect(self):
        pass
        # await self.base_connection.disconnect()
        # await self.base_controller.disconnect()

if __name__ == '__main__':
    unittest.main()
