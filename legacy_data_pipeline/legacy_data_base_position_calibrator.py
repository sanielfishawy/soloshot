# pylint: disable=C0413
import sys
import os
import numpy as np

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.tag_postion_in_stable_fov_segments_analyzer import TagPositionInStableFovSegmentsAnalyzer # pylint: disable=C0301
from legacy_data_pipeline.manual_visual_angle_calculator import ManualVisualAngleCalculator
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper
from legacy_data_pipeline.calibration_data_filer import CalibrationDataFiler
from video_and_photo_tools.image_from_video_grabber import ImageFromVideoGrabber

class LegacyDataBasePositionCalibrator:
    '''
    - Pulls frames using TagPositionInStableFovSegmentsAnalyzer.
    - Presents ManualVisualAngleCalculator to user to pinpoint tag in the two
      images for each frame and provide subtended visual angle.
    - Calculates the subtended angle using the subtended visual angle and difference
      in motor positions.
    - Generates circumcircles.
    '''

    def __init__(
            self,
            session_dir: str,
            tag_position_in_stable_fov_segments_analyzer: TagPositionInStableFovSegmentsAnalyzer,
            legacy_data_file_system_helper: LegacyDataFileSystemHelper,
            calibration_data_filer: CalibrationDataFiler,

            angle_threshold_rad=np.radians(10),
            frames_limit=None,
    ):
        self._session_dir = session_dir
        self._tag_postion_analyzer = tag_position_in_stable_fov_segments_analyzer
        self._ldfh = legacy_data_file_system_helper
        self._cdf = calibration_data_filer
        self._angle_threshold_rad = angle_threshold_rad
        self._frames_limit = frames_limit

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

    def _get_frames(self):
        if self._frames is None:
            self._frames = self._tag_postion_analyzer.get_frames_in_stable_fovs(
                angle_threshold_rad=self._angle_threshold_rad,
                limit=self._frames_limit,
            )
        return self._frames

    def _present_manual_visual_angle_calculator(self):
        for frame in self._get_frames():
            self._current_frame = frame
            fov = self._tag_postion_analyzer.get_fov_for_frame(frame)
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

    def _manual_angle_calculator_callback(self, angle_data):
        print(angle_data)
