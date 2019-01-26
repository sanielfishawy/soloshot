# pylint: disable=C0413
import sys
import os

sys.path.insert(0, os.getcwd())
from remote_control.request_response_object import RequestResponseObject

def connect():
    return RequestResponseObject('#CONNECT\n')

def disconnect():
    return RequestResponseObject('#QUIT\n')

def init():
    return RequestResponseObject('#INIT\n')

def deinit():
    return RequestResponseObject('#DEINIT\n')

def boot_controllers():
    return RequestResponseObject('#SEND,$105\n')

def enable_motors():
    return RequestResponseObject('#SEND,$61,B1,7,0,0\n')

def enable_debug_messages():
    return RequestResponseObject('#SEND,$61,B1,6,0,1\n')

def camera_on():
    return RequestResponseObject('#CAMERA,ON\n')

def camera_off():
    return RequestResponseObject('#CAMERA,OFF\n')

def pan_and_tilt_continously(pan_deg_per_sec, tilt_deg_per_sec=0):
    return RequestResponseObject(
        f'#SEND,$61,12,0,0,{pan_deg_per_sec * 10000},{tilt_deg_per_sec * 10000}\n'
    )
