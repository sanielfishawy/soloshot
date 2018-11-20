# pylint: disable=C0413
import sys
import os

sys.path.insert(0, os.getcwd())
from video_and_photo_tools.image_from_video import ImageFromVideo
from tk_canvas_renderers.vertical_image_list import VerticalImageList

class ManualVisualAngleCalculator:
    '''
    Displays images_from_video in vertical photo viewer.
    User pics position of object in both images.
    Returns subtended visual angle of the object from image_from_video_1 to image_from_video_2
    '''

    def __init__(
            self,
            image_from_video_1: ImageFromVideo,
            image_from_video_2: ImageFromVideo,
            fov_rad,
            callback,
    ):

        self._ifv_1 = image_from_video_1
        self._ifv_2 = image_from_video_2
        self._fov = fov_rad
        self._callback = callback


    def run(self):

