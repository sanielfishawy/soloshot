# pylint: disable=C0413
import sys
import os
sys.path.insert(0, os.getcwd())
from tests.test_moving_object_renderer import TestMovingObjectRenderer

TestMovingObjectRenderer().setUp().visualize()
