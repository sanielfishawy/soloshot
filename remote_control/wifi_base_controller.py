import argparse
import collections
import queue
import time
import asyncio
#from aioconsole import ainput
import re
import enum
import numpy as np
import cv2

np.set_printoptions(threshold=np.nan)

class CameraState(enum.Enum):
    powerOff = 0
    powerOn = 1
    idle = 2
    park = 3
    preview = 4
    record = 5


def get_current_time_in_ms():
    return time.time_ns() / 1000000


class PIDController:
    def __init__(self, p, i, d, name):
        self.kp = p
        self.ki = i
        self.kd = d
        self.name = name
        self.integral = 0
        self.lastVal = None
        self.lastTime_ms = get_current_time_in_ms()
        self.dataPoints = []

    def reset(self):
        self.lastVal = None
        self.lastTime_ms = get_current_time_in_ms()
        self.integral = 0

    def get_next_value(self, val):
        # print (self.name + " getting next value")
        if self.lastVal is None:
            print (self.name, " LastVal was None...")
            self.lastVal = val
            self.lastTime_ms = get_current_time_in_ms()
            derivative = 0
            self.integral = 0
        else:
            nowTime_ms = get_current_time_in_ms()
            derivative = (val - self.lastVal) / (nowTime_ms - self.lastTime_ms)
            self.integral += val * (nowTime_ms - self.lastTime_ms) / 1000.0
            self.lastTime_ms = nowTime_ms
            self.lastVal = val
        # print (self.name, " should be sending: ", self.kp * val + self.ki * self.integral + self.kd * derivative)
        # if self.name == "pan":
        #     print (self.name, "P:", self.kp, val, "\tI:", self.ki, self.integral, "\tD:", self.kd, derivative)
        return self.kp * val + self.ki * self.integral + self.kd * derivative

    def set_proportional(self, val):
        self.kp = val

    def set_integral(self, val):
        self.ki = val

    def set_derivative(self, val):
        self.kd = val

    def addDataPoint(self, pt, time):
        self.dataPoints.append([time, pt])

    def underdamped_harmonic_oscilator(self, t, amp, zeta, omega, phi):
        return amp * np.exp(-1 * zeta * omega * t) * np.sin(np.sqrt(1 - zeta * zeta) * omega * t + phi)

    def overdamped_term(self, sign, b, m, k):
        sign = sign / sign
        return (-1 * b + sign * np.sqrt(b * b - 4 * m * k)) / (2 * m)

    def overdamped_harmonic_oscilator(self, t, amp1, amp2, b, m, k):
        return amp1 * np.exp(self.overdamped_term(+1, b, m, k) * t) + amp2 * np.exp(
            self.overdamped_term(-1, b, m, k) * t)

    def get_coefficients(self, func, pars, bounds=(-np.inf, np.inf)):
        t = np.array([x[0] for x in self.dataPoints])
        v = np.array([x[1] for x in self.dataPoints])
        p, pcov = opt.curve_fit(func, t, v, p0=pars, bounds=bounds)
        return p

    def determine_underdamped(self):
        t = np.array([x[0] for x in self.dataPoints])
        v = np.array([x[1] for x in self.dataPoints])

    def fit_overdamped(self):
        return self.get_coefficients(self, self.overdamped_harmonic_oscilator, (-10, 0.5, 1, 0))

    def fit_underdamped(self):
        return self.get_coefficients(self, self.underdamped_harmonic_oscilator, (-10, 0.5, 1, 0))

class PIDUnitTester:
    def __init__(self):
        self.pid = PIDController(1, 0, 0, "test")

    def run_test(self, dataInput, expectedOutput, p, i , d):
        self.pid.set_proportional(p)
        self.pid.set_proportional(i)
        self.pid.set_proportional(d)
        for dataIn,out in zip(dataInput, expectedOutput):
            assert self.pid.get_next_value(dataIn) == out

def run_pid_unit_tests():
    pass

class CameraStateMachine():
    """Keeps state of camera and does transitions

    Attributes
    ----------
    cameraState : CameraState
        state of camera currently
    baseControl : BaseConnection
        Base controller with telnet connection
    """

    def __init__(self, baseControl):
        """
        PARAMETERS:
        ----------

        baseControl: BaseConnection
            base controller telnet connection
        """
        self.cameraState = CameraState.powerOff
        self.baseControl = baseControl

    async def transition(self, newState):
        #  Check if there is a transition
        if newState == self.cameraState:
            return
        #  There is a transition, so do transition
        if self.cameraState == CameraState.powerOff:
            await self.power_on()
        elif self.cameraState == CameraState.powerOn:
            if newState == CameraState.powerOff:
                await self.power_off()
            else:
                await self.idle()
        elif self.cameraState == CameraState.idle:
            if newState in (CameraState.powerOff, CameraState.powerOn, CameraState.park):
                await self.park()
            else:
                await self.preview()
        elif self.cameraState == CameraState.park:
            if newState == CameraState.powerOff:
                await self.power_off()
            elif newState == CameraState.powerOn:
                await self.power_on()
            else:
                await self.idle()
        elif self.cameraState == CameraState.preview:
            if newState == CameraState.record:
                await self.record_on()
            else:
                await self.idle()
        elif self.cameraState == CameraState.record:
            await self.record_off()
        else:
            print("In unallowable camera state:", self.cameraState)

        if self.cameraState != newState:
            await self.transition(newState)

    async def power_off(self):
        # call power off
        await self.baseControl.camera_command("OFF", confirmAction=False)
        self.cameraState = CameraState.powerOff

    async def power_on(self):
        # call power on
        await self.baseControl.camera_command("OFF", confirmAction=False)
        self.cameraState = CameraState.powerOn

    async def idle(self):
        # call go to idle
        await self.baseControl.camera_command("2")
        self.cameraState = CameraState.idle

    async def park(self):
        # call go to park
        await self.baseControl.camera_command("12")
        self.cameraState = CameraState.park

    async def preview(self):
        # call go to idle
        await self.baseControl.camera_command("4")
        self.cameraState = CameraState.preview

    async def record_on(self):
        # call go to idle
        await self.baseControl.camera_command("27")
        self.cameraState = CameraState.record

    async def record_off(self):
        # call go to idle
        await self.baseControl.camera_command("30")
        self.cameraState = CameraState.preview


DEFAULT_COMMAND_START_FRAMING_CHAR = "#"
DEFAULT_RESPONSE_FRAMING_CHAR = "&"
ASYNCHRONOUS_ACKNOWLEDGE_FRAMING_CHARACTER = "@"
MAX_RETRIES = 5
MAX_REQUESTS = 100

def dummyFunction():
    pass

class BaseConnection:

    def __init__(self, host, port, name, readSize=1024):
        self.host = host
        self.port = port
        self.name = name
        self.writer = None
        self.reader = None
        self.ack = False
        self.currentBuffer = ""
        self.sent_action = ""
        self.action_handled = False
        self.connected = False
        self.Error = None
        self.retryCount = 0
        self.camera_in_idle = True
        self.readSize = readSize
        self.read_buffer_deque = collections.deque(maxlen=100)
        self.requests_deque = collections.deque(maxlen=MAX_REQUESTS)
        self.motor_requests_deque = collections.deque(maxlen=1)
        self.activeRequest = False

    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            self.connected = True
        except (ConnectionRefusedError, TimeoutError, OSError) as e:
            print (e)
            self.connected = False
            await asyncio.sleep(2)
            print ("Failed to connect on  " + self.name + ", retrying ", self.retryCount)
            self.retryCount += 1
            if self.retryCount < MAX_RETRIES:
                return await self.connect()
            self.Error = e
            return False
        except Exception as e:
            self.Error = e
            return False
        except BaseException as e:
            self.Error = e
            return False
        except:
            print ("Thread for " + self.name + " crashed on connect is unknown way!!!")
        return True

    async def disconnect(self):
        if not self.connected:
            return True
        try:
            print ("About to send #QUIT on " + self.name)
            self.request("QUIT", confirmAction=False, postRequestAction=self.clean_up_disconnect)
        except IOError as e:
            self.Error = e
        except Exception as e:
            self.Error = e
        except BaseException as e:
            self.Error = e
        except:
            print("Thread for " + self.name + " crashed on disconnect is unknown way!!!")
        print ("set connected to False on " + self.name)
        return True

    async def clean_up_disconnect(self):
        print("self.writer.close() on " + self.name)
        self.writer.close()
        self.connected = False

    async def read(self):
        try:
            while not self.connected:
                await asyncio.sleep(1)
            while True:
                msg = await self.reader.read(self.readSize)
                if msg == b"":
                    print ("Nothing to read...")
                    await asyncio.sleep(0.1)
                    continue
                self.read_buffer_deque.append(msg)
        except Exception as e:
            self.Error = e
        finally:
            print (self.name, " Read raised Error and left while loop")

    async def handle_read_buffer(self, messageHandlerFunction):
        try:
            while True:
                try:
                    msg = self.read_buffer_deque.popleft()
                    await messageHandlerFunction(msg)
                except IndexError as e:
                    # print (self.name + ":  empty Deque")
                    await asyncio.sleep(0.1)
        except Exception as e:
            self.Error = e
        finally:
            print (self.name, " Handle Read Buffer raised Error and left while loop")

    #TODO:  Code still behaves linearly, need it to instead handle concurrent requests
    #TODO:  build a queueing system, with request always running, and pulling latest of queue
    #TODO:  queue item = {"msg": "blahBlah", "confirmAck"=True, "confirmAction"=False, "maxWait"=10, "sleepTime"=0.1, "debug"=True}

    def request(self, msg, confirmAck=True, confirmAction=True, maxWait = 10, sleepTime=0.1, motorRequest=False, debug=False, postRequestAction=dummyFunction):
        if motorRequest:
            self.motor_requests_deque.append({"msg": msg,
                                              "confirmAck": confirmAck,
                                              "confirmAction": confirmAction,
                                              "maxWait": maxWait,
                                              "sleepTime": sleepTime,
                                              "debug": debug,
                                              "postRequestAction": postRequestAction})
        else:
            self.requests_deque.append({"msg": msg,
                                        "confirmAck": confirmAck,
                                        "confirmAction": confirmAction,
                                        "maxWait": maxWait,
                                        "sleepTime": sleepTime,
                                        "debug": debug,
                                        "postRequestAction": postRequestAction})
        if len(self.requests_deque) > MAX_REQUESTS / 2:
            pass
        print ("There are", len(self.requests_deque), " items in the request queue", msg)
        if len(self.requests_deque) == MAX_REQUESTS:
            raise IndexError("Too many items in queue")

    async def run_requests(self):
        # while True:
        request = None
        try:
            request = self.requests_deque.popleft()
        except IndexError as e:
            try:
                request = self.motor_requests_deque.popleft()
            except IndexError as e:
                await asyncio.sleep(0.01)
        except Exception as e:
            self.Error = e
        except:
            print ("run_requests died with unknown error")
        if request is not None:
            print ("running ", request)
            self.ack = False
            self.action_handled = False
            self.sent_action = request["msg"]
            msg = DEFAULT_COMMAND_START_FRAMING_CHAR + request["msg"] + "\n"
            if request["debug"]:
                print (self.name + " writing msg: " + msg)
            self.writer.write(msg.encode())
            await self.writer.drain()
            if request["confirmAck"]:
                gotAck = await self.got_ack(request["maxWait"], request["sleepTime"])
                if request["debug"]: print ("Recognized Ack")
            if request["confirmAction"]:
                confirmed = False
                while not confirmed:
                    confirmed = await self.wait_for_action_confirmation(request["maxWait"], request["sleepTime"])
                    if not confirmed:  print ("not confirmed Action")
                if request["debug"]:
                    print ("confirmed Action: ", confirmed)
            if request["debug"]:
                print ("Done Request on " + self.name)
            request["postRequestAction"]()

    async def conn(self):
        while not self.connected:
            await asyncio.sleep(1)
        print ("Trying #CONNECT on " + self.name)
        self.request("CONNECT", confirmAction=False)

    async def got_ack(self, maxWait = 5, sleepTime=0.1):
        wait = 0.0
        while not self.ack:
            #print ("Waiting for ack:", wait)
            await asyncio.sleep(sleepTime)
            wait += sleepTime
            if wait > maxWait:
                print ("Failed to get Ack on " + self.name + " for", self.sent_action)
                wait = 0.0
            return False
        return True

    async def wait_for_action_confirmation(self, maxWait = 5, sleepTime=0.1):
        wait = 0.0
        while not self.action_handled:
            # print ("waiting in wait_for_action_confirmation")
            await asyncio.sleep(sleepTime)
            wait += sleepTime
            if wait > maxWait:
                print ("Failed to get action confirmation for", self.sent_action)
                return False
        return True

    def check_send_response(self, msg):
        # print ("Got a # on " + self.name + ":" , msg)
        if msg == "ACK":
            self.ack = True
        else:
            print ("Abnormal message on " + self.name + ": ", msg)

    def record_action(self, msg):
        # print (self.sent_action == msg, self.sent_action, len(self.sent_action), msg, len(msg), sum([ord(x) for x in self.sent_action]), sum([ord(x) for x in msg]), [ord(x) for x in self.sent_action], [ord(x) for x in msg])
        if self.sent_action == msg:
            # print ("Set self.sent_action to True for:",msg)
            self.action_handled = True

    def set_host(self, host):
        self.host = host
    def set_port(self, port):
        self.port = port

class BasePosition:
    def __init__(self, pan=0.0, tilt=0.0):
        self.pan = pan
        self.tilt = tilt

    def set_pan(self, pan):
        self.pan = pan
    def set_tilt(self, tilt):
        self.tilt = tilt

class BaseController(BaseConnection):

    class BaseState(enum.Enum):
        DISCONNECTED = 0
        CONNECTED = 1
        INITIALIZED = 2
        BOOTED = 3

    def __init__(self, host, port):
        BaseConnection.__init__(self, host, port, "base control")
        self.baseCurrentPosition = BasePosition()
        self.baseCurrentStep = BasePosition(3,3)
        self.baseSetPosition = BasePosition()
        self.baseSetTime = BasePosition(3,3)
        self.camera_power_on = False
        self.motors_updated = False
        self.print_motors = False
        self.print_camera = False
        self.panPid = PIDController(0.3, 0, 0, "pan")
        self.tiltPid = PIDController(0.3, 0, 0, "tilt")
        self.state = self.BaseState.DISCONNECTED

    def toggle_print_motors(self):
        self.print_motors = not self.print_motors

    def toggle_camera_motors(self):
        self.print_camera = not self.print_camera

    #  Set up related commands
    async def init(self):
        # print ("Trying #INIT")
        self.request("INIT", postRequestAction=self.set_base_state_initialized)
        return

    async def deinit(self):
        # print ("Trying #INIT")
        self.request("DEINIT", postRequestAction=self.set_base_state_connected)
        return

    def set_base_state_initialized(self):
        self.state = self.BaseState.INITIALIZED

    def set_base_state_connected(self):
        self.state = self.BaseState.CONNECTED

    async def send_command(self, command):
        com = "SEND," + command
        # print ("Trying "+str(com)+" on "+self.name)
        self.request(com)

    async def disconnect(self):
        if self.state == self.BaseState.DISCONNECTED:
            return
        if self.state == self.BaseState.BOOTED or self.state == self.BaseState.INITIALIZED:
            await self.deinit()
        if self.state == self.BaseState.CONNECTED:
            await BaseConnection.disconnect()
            self.state = self.BaseState.DISCONNECTED
        else:
            print ("Should be in connected state, but are actually in", self.state.name)
            await self.disconnect()


    async def send_k20_init(self):
        try:
            await self.conn()
            await asyncio.sleep(2)
            self.state = self.BaseState.CONNECTED
            await self.init()
            await asyncio.sleep(2)
            await self.send_command("$105")
            await asyncio.sleep(2)
        except IOError as e:
            self.Error = e
        except Exception as e:
            self.Error = e
        print("Base initializations command sent")
        return True

    async def handle_msg(self, msg):
        self.currentBuffer += msg.decode()
        while "\n" in self.currentBuffer:
            startCharacter = self.currentBuffer[0]
            newMsg, self.currentBuffer = self.currentBuffer.split(startCharacter + '\n', 1)
            print ("New Message on " + self.name + ":", newMsg)
            if startCharacter == DEFAULT_COMMAND_START_FRAMING_CHAR:
                self.check_send_response(newMsg[1:])
            elif startCharacter == DEFAULT_RESPONSE_FRAMING_CHAR:
                self.record_action(newMsg[1:])
            elif startCharacter == ASYNCHRONOUS_ACKNOWLEDGE_FRAMING_CHARACTER:
                await self.record_feedback(newMsg[1:])
            else:
                self.record_no_header(newMsg)

    #  Asynchronous data handling
    async def record_feedback(self, msg):
        if msg.startswith("MOTOR"):
            self.extract_motor_info(msg)
            return
        print("New Message to record" + self.name + ":", msg)
        if msg.startswith("CAMERA"):
            self.extract_camera_info(msg)
            return

    #  Asynchronous data handling
    def record_no_header(self, msg):
        print("New Message to with unknown header on "+self.name+":", msg)

    #  Stream related commands
    async def toggle_setting(self, setting, ):
        com = "TOGGLE," + setting
        print("Trying " + str(com))
        self.request(com, confirmAction=False)

    async def toggle_base_sensor_fusion(self):
        return await self.toggle_setting("SF")

    async def toggle_tag_radio(self):
        return await self.toggle_setting("RADIO")

    async def toggle_base_gps(self):
        return await self.toggle_setting("GPS")

    def safe_delta_pan(self, pan):
        newPan = pan if pan < 90 else 90
        newPan = newPan if newPan > -90 else -90
        return newPan

    def bounded_pan(self, pan):
        while pan < -180:
            pan += 360.0
        while pan > 180:
            pan -= 360.0
        return pan

    def safe_tilt(self, tilt):
        safeTilt = tilt if tilt < 90 else 90
        safeTilt = safeTilt if safeTilt > -50 else -50
        return safeTilt

    #  Motor related commands
    async def move_motors(self):
        try:
            while True:
                if self.state == self.BaseState.BOOTED:
                    panChange = self.panPid.get_next_value(self.bounded_pan(self.baseSetPosition.pan - self.baseCurrentPosition.pan))
                    tiltChange = self.tiltPid.get_next_value(self.baseSetPosition.tilt - self.baseCurrentPosition.tilt)
                    com = "MOTOR,{:f},{:f},{:d},{:d}".format(self.bounded_pan(self.baseSetPosition.pan + self.safe_delta_pan(panChange)),
                                                             self.safe_tilt(self.baseSetPosition.tilt + tiltChange),
                                                             int(self.baseSetTime.pan),
                                                             int(self.baseSetTime.tilt))

                    if self.print_motors:
                        print("Input:  " + str(com))
                    self.request(com, confirmAck=False, confirmAction=False, motorRequest=True)
                    await asyncio.sleep(0.1)
                    # print ("motor request done")
                else:
                    await asyncio.sleep(0.1)
        except Exception as e:
            print ("Motor Error")
            self.Error = e
        finally:
            print ("Motor loop ended for some reason!")

    def set_motors(self, pan, tilt, pan_time, tilt_time):
        self.baseSetPosition.set_pan(pan)
        self.baseSetPosition.set_tilt(tilt)
        self.baseSetTime.set_pan(pan_time)
        self.baseSetTime.set_tilt(tilt_time)

    def set_motors_delta(self, deltaPan, deltaTilt, deltaPanTime, deltaTiltTime):
        self.baseSetPosition.set_pan(self.baseSetPosition.pan + deltaPan)
        self.baseSetPosition.set_tilt(self.baseSetPosition.tilt + deltaTilt)
        self.baseSetTime.set_pan(deltaPanTime)
        self.baseSetTime.set_tilt(deltaTiltTime)

    def extract_motor_info(self, msg):
        if self.print_motors:
            print ("MOTORS: ", msg)
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", msg)
        if len(numbers) == 4:
            self.baseCurrentPosition.set_pan(float(numbers[0]))
            self.baseCurrentPosition.set_tilt(float(numbers[2]))  #TODO: fix when motor message is corrected
            self.baseCurrentStep.set_pan(numbers[2])
            self.baseCurrentStep.set_tilt(numbers[3])
            self.motors_updated = True

    #  Camera related commands
    async def camera_command(self, command, confirmAck=True, confirmAction=True):
        com = "CAMERA," + command
        print("Trying " + str(com))
        self.request(com, confirmAck=confirmAck, confirmAction=confirmAction, debug=True)
        # TODO: some kind of check that camera is ready for the next command and in the correct state
        # TODO: and send it as post process check to be awaited.

    def extract_camera_info(self, msg):
        if self.print_camera:
            print ("CAMERA: ", msg)
        msg_info = msg.split(',',3)[1:]
        if "Notification" in msg_info[1]:
            return self.extract_camera_notification_info(msg_info[2])
        if "Status" in msg_info[1]:
            return self.extract_camera_status_info(msg_info[2])

    def extract_camera_notification_info(self, msg):
        if "boot_done" in msg:
            self.state = self.BaseState.BOOTED
            print ("Base Control Initialization Done")

    def extract_camera_status_info(self, msg):
        pass

    async def toggle_camera_power(self):
        while not self.state == self.BaseState.BOOTED:
            await asyncio.sleep(3)
        if self.camera_power_on:
            await self.camera_command("OFF", confirmAction=False)
        else:
            await self.camera_command("ON", confirmAction=False)
            await self.camera_command("1", confirmAction=False)  # enter_idle
            self.camera_in_idle = True
        self.camera_power_on = not self.camera_power_on

    async def toggle_camera_preview(self):
        try:
            print ("In the toggle camera preview")
            if not self.camera_power_on:
                await self.toggle_camera_power()
            value = "3" if self.camera_in_idle else "1"
            await self.camera_command(value, confirmAction=False)
            self.camera_in_idle = not self.camera_in_idle
        except Exception as e:
            print ("Error during toggle_camera_preview")
            self.Error = e

class VideoController(BaseConnection):

    def __init__(self, host, port, videoSize=(320,240)):
        BaseConnection.__init__(self, host, port, "video control", readSize=1024)#videoSize[0]*videoSize[1]*3)
        self.frame_queue = queue.Queue(100)
        self.frame_iter = 0
        self.gotFrame = False
        self.connectAcked = False
        self.videoSize = (videoSize[0], videoSize[1])
        self.packetSize = self.videoSize[0] * self.videoSize[1] * 3 // 2
        self.readSize = self.packetSize
        self.frames = 0
        self.framesSinceLastTime = 0
        self.startTime = 0
        self.lastTime = 0

        #  Video will be BGR in the end, but is shipped over as YUV (I420).
        #  YUV is some weird 1.5 pixel thing, so we need to grab h*w*2/3 bytes
        #  Then this must be reshaped as h=240*3/2, w=320
        #  Then, it must be converted to BRG as cv2.cvtColor(yuv_reshaped, cv2.COLOR_YUV2BGR_I420)

    async def init(self):
        try:
            await self.conn()
            await asyncio.sleep(2)
        except IOError as e:
            self.Error = e
        except Exception as e:
            self.Error = e
        print("Video Connected")

    async def handle_msg(self, msg):
        # print (len(msg))
        if not self.connectAcked:
            self.currentBuffer += msg.decode()
            # print ("Got this on video:", msg, self.currentBuffer)
            while "\n" in self.currentBuffer:
                startCharacter = self.currentBuffer[0]
                newMsg, self.currentBuffer = self.currentBuffer.split(startCharacter + '\n', 1)
                # print("New Message on " + self.name + ":", newMsg)
                if startCharacter == DEFAULT_COMMAND_START_FRAMING_CHAR:
                    self.check_send_response(newMsg[1:])
            self.connectAcked = self.ack
            self.currentBuffer = b''
        else:
            self.handle_video(msg)

    def handle_video(self, msg):
        self.currentBuffer += msg
        if len(self.currentBuffer) < self.packetSize:
            return
        #  Convert buffer here, or in CV buffer?  For now try here
        # npArr = np.fromstring(self.currentBuffer[:self.packetSize], np.uint8)
        self.frames += 1
        self.framesSinceLastTime += 1
        self.frame_queue.put(self.currentBuffer[:self.packetSize])
        if not self.gotFrame:
            self.startTime = time.time()
            self.lastTime = time.time()
        self.gotFrame = True
        self.currentBuffer = self.currentBuffer[self.packetSize:]
        if self.frames % 100 == 99:
            print ("FrameRate:", self.framesSinceLastTime / (time.time() - self.lastTime), self.frames / (time.time() - self.startTime))
            self.lastTime = time.time()
            self.framesSinceLastTime = 0

def parse_command_line_args():
    parser = argparse.ArgumentParser(description="parsing arguments")
    parser.add_argument('-i', '--ip',
                        action='store',
                        dest='ip',
                        help='base ip address (see "Settings > Developer Options > WIFI IP")'
    )
    parser.add_argument('-t', '--tests',
                        action='store_true',
                        dest='tests',
                        help='Run unit tests on PID'
    )
    return parser.parse_args()

def validate_ip(ip):
    while ip is None:
        ip = input('Enter base ip.  It can be found in "Settings > Developer Options > WIFI IP": ')
        ip = str(ip)
        if ip == '':
            ip = None
    return ip

def main():
    args = parse_command_line_args()

    if args.tests:
        run_pid_unit_tests()
        return

    ip = validate_ip(args.ip)

    h = BaseConnection(ip, 8080)

    # asyncio.get_event_loop().create_task(h.connect())
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(h.connect())
    print ("Connection established:  ", h.reader, h.writer)
    read = asyncio.ensure_future(h.read())
    write = asyncio.ensure_future(h.send_k20_init())
    loop.run_forever()
    loop.close()


if __name__ == '__main__':
    main()