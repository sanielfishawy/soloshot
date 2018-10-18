# pylint: disable=C0413
import sys
import os
sys.path.insert(0, os.getcwd())
from tests.test_vertical_image_list import TestVerticalImageList

TestVerticalImageList().setUp().visualize()
