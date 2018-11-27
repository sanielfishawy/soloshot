# pylint: disable=C0413
import sys
import os

sys.path.insert(0, os.getcwd())
from video_and_photo_tools.image_from_video import ImageFromVideo
from tk_canvas_renderers.vertical_image_list import VerticalImageList
import visual_angle_calculator as Vac

class ManualVisualAngleCalculator:
    '''
    Displays images_from_video in vertical photo viewer.
    User pics position of object in both images.
    Returns subtended visual angle of the object from image_from_video_1 to image_from_video_2
    '''

    FOV = 'fov'
    IMAGE_WIDTH = 'image_width'
    X_POS_1 = 'x_pos_1'
    X_POS_2 = 'x_pos_2'
    ANGLE_TO_CENTER_1 = 'angle_to_center_1'
    ANGLE_TO_CENTER_2 = 'angle_to_center_2'
    SUBTENDED_ANGLE = 'subtended_angle'

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

        self._image_width = self._ifv_1.get_image().width

        self._vertical_image_list = VerticalImageList(
            images_from_video=[self._ifv_1, self._ifv_2],
            callback=self._vertical_image_list_callback,
        )

    def _vertical_image_list_callback(self, selected_points):
        x_1 = selected_points[0][VerticalImageList.SELECTED_POINT][0]
        x_2 = selected_points[1][VerticalImageList.SELECTED_POINT][0]

        self._callback(
            angle_data={
                self.__class__.FOV: self._fov,
                self.__class__.IMAGE_WIDTH: self._image_width,
                self.__class__.X_POS_1: selected_points[0][VerticalImageList.SELECTED_POINT][0],
                self.__class__.X_POS_2: selected_points[1][VerticalImageList.SELECTED_POINT][0],
                self.__class__.ANGLE_TO_CENTER_1: Vac.get_angle_relative_to_center_with_x_rad(
                    x_pos=x_1,
                    image_width=self._image_width,
                    fov_rad=self._fov,
                ),
                self.__class__.ANGLE_TO_CENTER_2: Vac.get_angle_relative_to_center_with_x_rad(
                    x_pos=x_2,
                    image_width=self._image_width,
                    fov_rad=self._fov,
                ),
                self.__class__.SUBTENDED_ANGLE: Vac.get_subtended_angle_with_x_rad(
                    x_1=x_1,
                    x_2=x_2,
                    image_width=self._image_width,
                    fov_rad=self._fov,
                ),
            }
        )


    def run(self):
        self._vertical_image_list.run()
