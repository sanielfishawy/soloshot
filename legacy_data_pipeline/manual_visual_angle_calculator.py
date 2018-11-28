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
    Returns VisualAngleData from image_from_video_1 to image_from_video_2
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

        self._image_width = self._ifv_1.get_image().width

        self._vertical_image_list = VerticalImageList(
            images_from_video=[self._ifv_1, self._ifv_2],
            callback=self._vertical_image_list_callback,
        )

    def _vertical_image_list_callback(self, selected_points):
        x_1 = selected_points[0][VerticalImageList.SELECTED_POINT][0]
        x_2 = selected_points[1][VerticalImageList.SELECTED_POINT][0]

        self._callback(
            VisualAngleData(
                x_pos_1=x_1,
                x_pos_2=x_2,
                image_width=self._image_width,
                fov=self._fov,
            )
        )

    def run(self):
        self._vertical_image_list.run()


class VisualAngleData:

    def __init__(
            self,
            fov,
            image_width,
            x_pos_1,
            x_pos_2,
    ):

        self._fov = fov
        self._image_width = image_width
        self._x_pos_1 = x_pos_1
        self._x_pos_2 = x_pos_2

        # lazy inits
        self._subtended_angle = None
        self._angle_to_center_1 = None
        self._angle_to_center_2 = None


    def get_fov(self):
        return self._fov

    def get_image_width(self):
        return self._image_width

    def get_x_pos_1(self):
        return self._x_pos_1

    def get_x_pos_2(self):
        return self._x_pos_2

    def get_angle_to_center_1(self):
        if self._angle_to_center_1 is None:
            self._angle_to_center_1 = Vac.get_angle_relative_to_center_with_x_rad(
                x_pos=self.get_x_pos_1,
                image_width=self.get_image_width(),
                fov_rad=self.get_fov(),
            )
        return self._angle_to_center_1

    def get_angle_to_center_2(self):
        if self._angle_to_center_2 is None:
            self._angle_to_center_2 = Vac.get_angle_relative_to_center_with_x_rad(
                x_pos=self.get_x_pos_2,
                image_width=self.get_image_width(),
                fov_rad=self.get_fov(),
            )
        return self._angle_to_center_2

    def get_subtended_angle(self):
        if self._subtended_angle is None:
            self._subtended_angle = Vac.get_subtended_angle_with_x_rad(
                x_1=self.get_x_pos_1(),
                x_2=self.get_x_pos_2(),
                image_width=self.get_image_width(),
                fov_rad=self.get_fov(),
            )
        return self._subtended_angle
