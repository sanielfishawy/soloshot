import math

import geometry_utils as GU
from base_position_calibrator import BasePositionCalibrator
from camera import Camera
from object_motion_analyzer import ObjectMotionAnalyzer
from tag_position_analyzer import TagPositionAnalyzer

class BaseAngleCalibrator:
    
    def __init__(self, base_position_calibrator):
        '''
        :param BasePositionCalibrator base_position_calibrator:
        '''
        self._base_position_calibrator = base_position_calibrator
        self._get_tag() # Forces initialization of base_position_calculator and classes it uses.

    def get_base_angle_error(self):
        r = self._get_actual_camera_angle() - self._get_camera_motor_angle()
        if r > 2 * math.pi:
            r = r - 2*math.pi
        return r

    def get_object_motion_analyzer(self):
        '''
        :rtype ObjectMotionAnalyzer
        '''
        return self._base_position_calibrator.get_object_motion_analyzer()

    def get_tag_position_analyzer(self):
        '''
        :rtype TagPositionAnalyzer
        '''
        return self.get_object_motion_analyzer().get_tag_position_analyzer()
    
    def get_camera(self):
        '''
        :rtype Camera
        '''
        return self._base_position_calibrator.get_camera()

    def _get_tag(self):
        return self._base_position_calibrator.get_tag_candidate()

    def _get_timestamp(self):
        return self.get_tag_position_analyzer().get_early_min_max_timestamp(self._get_frame())

    def _get_camera_position(self):
        return self._base_position_calibrator.get_base_position()
    
    def _get_camera_motor_angle(self):
        return self.get_camera().get_motor_pan_angle_rad(self._get_timestamp())

    def _get_frame(self):
        return self.get_object_motion_analyzer().get_first_frame_with_object(self._get_tag())

    def _get_tag_position(self):
        return self.get_tag_position_analyzer().get_early_position(self._get_frame())
    
    def _get_tag_angle_relative_to_center_in_image(self):
        return self.get_object_motion_analyzer().get_early_angle_relative_to_center_for_object_in_frame(self._get_tag(), self._get_frame())

    def _get_gps_angle_from_camera_to_tag_360(self):
        return GU.angel_of_vector_between_points_360_rad(self._get_camera_position(), self._get_tag_position())
    
    def _get_actual_camera_angle(self):
        return self._get_gps_angle_from_camera_to_tag_360() - self._get_tag_angle_relative_to_center_in_image()
    
