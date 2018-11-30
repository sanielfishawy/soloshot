# pylint: disable=C0413
import sys
import os
import numpy as np

sys.path.insert(0, os.getcwd())
from base import Base
from legacy_data_pipeline.tag_postion_in_stable_fov_segments_analyzer import TagPositionInStableFovSegmentsAnalyzer # pylint: disable=C0301
from legacy_data_pipeline.manual_visual_angle_calculator import ManualVisualAngleCalculator, VisualAngleData # pylint: disable=C0301
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper
from legacy_data_pipeline.calibration_data_filer import CalibrationDataFiler
import legacy_data_pipeline.pan_motor_angle_calculator as PanAngleCalculator
from video_and_photo_tools.image_from_video_grabber import ImageFromVideoGrabber
from circumcircles import Circumcircles

class LegacyDataBasePositionCalibrator:
    '''
    - Pulls frames using TagPositionInStableFovSegmentsAnalyzer.
    - Presents ManualVisualAngleCalculator to user to pinpoint tag in the two
      images for each frame and provide subtended visual angle.
    - Calculates the subtended angle using the subtended visual angle and difference
      in motor positions.
    - Generates circumcircles.
    '''

    FRAME = 'frame'
    VISUAL_ANGLE_DATA = 'visual_angle_data'
    MOTOR_ANGLE_DATA = 'motor_angle_data'
    COMBINED_ANGLE_DATA = 'combined_angle_data'
    CIRCUMCIRCLES = 'circumcircles'

    def __init__(
            self,
            session_dir: str,
            tag_position_in_stable_fov_segments_analyzer: TagPositionInStableFovSegmentsAnalyzer,
            legacy_data_file_system_helper: LegacyDataFileSystemHelper,
            calibration_data_filer: CalibrationDataFiler,

            angle_threshold_rad=np.radians(10),
            frames_limit=None,
            min_distance_to_camera=80, # pixels after transformation.
    ):
        self._session_dir = session_dir
        self._tag_postion_analyzer = tag_position_in_stable_fov_segments_analyzer
        self._ldfh = legacy_data_file_system_helper
        self._cdf = calibration_data_filer
        self._angle_threshold_rad = angle_threshold_rad
        self._frames_limit = frames_limit
        self._min_distance_to_camera = min_distance_to_camera

        # helpers
        self._image_from_video_grabber = ImageFromVideoGrabber(
            video_path=self._ldfh.get_video_path(self._session_dir)
        )

        # convenience
        self._tag = self._tag_postion_analyzer.get_tag()
        self._base = self._tag_postion_analyzer.get_base()

        # lazy inits
        self._frames = None

        # state
        self._current_frame = None # Because ManualVisualAngleCalculator calls back and context is lost
        self._results = []

    def _get_frames(self):
        if self._frames is None:
            self._frames = self._tag_postion_analyzer.get_frames_in_stable_fovs(
                angle_threshold_rad=self._angle_threshold_rad,
                min_distance_to_camera=self._min_distance_to_camera,
                limit=self._frames_limit,
            )
        return self._frames

    def _present_manual_visual_angle_calculator(self):
        for frame in self._get_frames():
            self._current_frame = frame
            fov = np.radians(self._tag_postion_analyzer.get_fov_for_frame(frame))
            ManualVisualAngleCalculator(
                image_from_video_1=self._get_early_image_from_video_for_frame(frame),
                image_from_video_2=self._get_late_image_from_video_for_frame(frame),
                fov_rad=fov,
                callback=self._manual_angle_calculator_callback,
            ).run()

    def _get_early_image_from_video_for_frame(self, frame):
        tag_timestamp = self._tag_postion_analyzer.get_early_min_max_timestamp(frame)
        return self._get_image_at_tag_timestamp(tag_timestamp)

    def _get_late_image_from_video_for_frame(self, frame):
        tag_timestamp = self._tag_postion_analyzer.get_late_min_max_timestamp(frame)
        return self._get_image_at_tag_timestamp(tag_timestamp)

    def _get_image_at_tag_timestamp(self, tag_timestamp):
        video_time = self._tag.get_video_time_for_timestamp(tag_timestamp)
        return self._image_from_video_grabber.get_image_from_video_at_time_ms(video_time)

    def _manual_angle_calculator_callback(self, visual_angle_data: VisualAngleData):
        motor_angle_data = MotorAngleData(
            early_video_time=self._tag.get_video_time_for_timestamp(
                self._tag_postion_analyzer.get_early_min_max_timestamp(self._current_frame)
            ),
            late_video_time=self._tag.get_video_time_for_timestamp(
                self._tag_postion_analyzer.get_late_min_max_timestamp(self._current_frame)
            ),
            base=self._base,
        )

        combined_angle_data = CombinedAngleData(
            motor_angle_data=motor_angle_data,
            visual_angle_data=visual_angle_data,
        )

        circumcircles = Circumcircles(
            early_postion=self._tag_postion_analyzer.get_early_position(self._current_frame),
            late_position=self._tag_postion_analyzer.get_late_position(self._current_frame),
            theta_rad=combined_angle_data.get_combined_subtended_angle(),
            error_circle_center=self._base.get_x_y_gps_position(),
            error_circle_radius=self._base.get_base_gps_error_circle_radius_pixels(),
        )

        self._results.append(
            {
                self.__class__.VISUAL_ANGLE_DATA: visual_angle_data,
                self.__class__.FRAME: self._current_frame,
                self.__class__.MOTOR_ANGLE_DATA: motor_angle_data,
                self.__class__.COMBINED_ANGLE_DATA: combined_angle_data,
                self.__class__.CIRCUMCIRCLES: circumcircles,
            }
        )


    def run(self):
        self._present_manual_visual_angle_calculator()
        return self._results

    def get_all_frames(self):
        return [
            result[self.__class__.FRAME]
            for result in self.get_results()
        ]

    def get_results(self):
        return self._results

    def get_all_error_circle_intersections(self):
        return [
            circumcircle.get_error_circle_intersection()
            for circumcircle in self.get_all_circumcircle_objects()
        ]

    def get_all_c1s_low_def(self):
        return [
            circumcircle.get_c1_low_def()
            for circumcircle in self.get_all_circumcircle_objects()
        ]

    def get_all_c2s_low_def(self):
        return [
            circumcircle.get_c2_low_def()
            for circumcircle in self.get_all_circumcircle_objects()
        ]

    def get_all_circumcircle_objects(self):
        return [
            result[self.__class__.CIRCUMCIRCLES]
            for result in self.get_results()
        ]

class MotorAngleData:

    def __init__(
            self,
            base: Base,
            early_video_time,
            late_video_time,
    ):

        self._base = base
        self._early_video_time = early_video_time
        self._late_video_time = late_video_time

        # lazy inits
        self._early_motor_angle_rad = None
        self._late_motor_angle_rad = None
        self._subtended_motor_angle_rad = None


    def get_base(self):
        return self._base

    def get_early_video_time(self):
        return self._early_video_time

    def get_late_video_time(self):
        return self._late_video_time

    def get_early_motor_angle_rad(self):
        if self._early_motor_angle_rad is None:
            self._early_motor_angle_rad = self.get_base().get_motor_angle_for_video_time_rad(
                self.get_early_video_time()
            )
        return self._early_motor_angle_rad

    def get_late_motor_angle_rad(self):
        if self._late_motor_angle_rad is None:
            self._late_motor_angle_rad = self.get_base().get_motor_angle_for_video_time_rad(
                self.get_late_video_time()
            )
        return self._late_motor_angle_rad

    def get_subtended_motor_angle(self):
        return PanAngleCalculator.get_acute_subtened_motor_angle_rad(
            early_angle_rad=self.get_early_motor_angle_rad(),
            late_angle_rad=self.get_late_motor_angle_rad(),
        )

class CombinedAngleData:
    def __init__(
            self,
            motor_angle_data: MotorAngleData,
            visual_angle_data: VisualAngleData,
    ):
        self._motor_angle_data = motor_angle_data
        self._visual_angle_data = visual_angle_data

    def get_combined_subtended_angle(self):
        return self._motor_angle_data.get_subtended_motor_angle() + \
               self._visual_angle_data.get_subtended_angle()
