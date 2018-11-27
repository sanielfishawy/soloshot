# pylint: disable=C0413, W0212
import sys
import os
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.legacy_data_base_position_calibrator import LegacyDataBasePositionCalibrator # pylint: disable=C0301
from legacy_data_pipeline.tag_postion_in_stable_fov_segments_analyzer import TagPositionInStableFovSegmentsAnalyzer # pylint: disable=C0301
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper as LDFH
from legacy_data_pipeline.calibration_data_filer import CalibrationDataFiler as CDF
from geo_mapping.geo_mapper import MapFitter, MapCoordinateTransformer
from tag import Tag
from base import Base

class TestLegacyDataBasePositionCalibrator(unittest.TestCase):

    def setUp(self):
        head_path = Path('/Volumes/WD')
        session_dir = 'Aug_17_Palo_Alto_High_2nd_time_B80_ottofillmore'
        results_head_path = Path('.')  / 'data/calibration_data',

        ldfh = LDFH(
            head_path=head_path,
        )
        cdf = CDF(
            top_level_dir=results_head_path
        )

        fov_series = ldfh.get_field_from_npz_file(
            session_dir_name=session_dir,
            filename=LDFH.LENS_NPZ_FILE,
            fieldname=LDFH.LENS_FOV_FIELD,
        )
        fov_time_series = ldfh.get_field_from_npz_file(
            session_dir_name=session_dir,
            filename=LDFH.LENS_NPZ_FILE,
            fieldname=LDFH.LENS_TIME_FIELD,
        )
        tag_latitude_series = ldfh.get_field_from_npz_file(
            session_dir_name=session_dir,
            filename=LDFH.TAG_NPZ_FILE,
            fieldname=LDFH.TAG_LATITUDE_FIELD,
        )
        tag_longitude_series = ldfh.get_field_from_npz_file(
            session_dir_name=session_dir,
            filename=LDFH.TAG_NPZ_FILE,
            fieldname=LDFH.TAG_LONGITUDE_FIELD,
        )
        tag_time_series = ldfh.get_field_from_npz_file(
            session_dir_name=session_dir,
            filename=LDFH.TAG_NPZ_FILE,
            fieldname=LDFH.TAG_TIME_FIELD,
        )

        map_fitter = MapFitter(
            latitude_series=tag_latitude_series,
            longitude_series=tag_longitude_series,
        )

        map_coordinate_transformer = MapCoordinateTransformer.init_with_map_fitter(
            map_fitter=map_fitter,
        )

        tag = Tag(
            latitude_series=tag_latitude_series,
            longitude_series=tag_longitude_series,
            time_series=tag_time_series,
            alignment_offset_video_to_tag_ms=-57, # From calibration data
            map_coordinate_transformer=map_coordinate_transformer,
        )

        base_gps_latitude = ldfh.get_field_from_npz_file(
            session_dir_name=session_dir,
            filename=LDFH.TAG_NPZ_FILE,
            fieldname=LDFH.BASE_LATITUDE_FIELD,
        )
        base_gps_longitude = ldfh.get_field_from_npz_file(
            session_dir_name=session_dir,
            filename=LDFH.TAG_NPZ_FILE,
            fieldname=LDFH.BASE_LONGITUDE_FIELD,
        )
        base_time_series = tag_time_series

        pan_motor_angle_series = ldfh.get_field_from_npz_file(
            session_dir_name=session_dir,
            filename=LDFH.BASE_NPZ_FILE,
            fieldname=LDFH.PAN_MOTOR_READ_FIELD,
        )

        base = Base(
            gps_latitude_series=base_gps_latitude,
            gps_longitude_series=base_gps_longitude,
            base_time_series=base_time_series,
            map_coordinate_transformer=map_coordinate_transformer,
            pan_motor_angle_series=pan_motor_angle_series,
        )

        tag_position_analyzer = TagPositionInStableFovSegmentsAnalyzer(
            fov_series=fov_series,
            fov_time_series=fov_time_series,
            tag=tag,
            base=base,
        )

        self.legacy_data_base_position_calibrator = LegacyDataBasePositionCalibrator(
            session_dir=session_dir,
            tag_position_in_stable_fov_segments_analyzer=tag_position_analyzer,
            legacy_data_file_system_helper=ldfh,
            calibration_data_filer=cdf,
            frames_limit=8,
            angle_threshold_rad=np.radians(20),
            min_distance_to_camera=100,
        )

    def test(self):
        self.legacy_data_base_position_calibrator._present_manual_visual_angle_calculator()


if __name__ == '__main__':
    unittest.main()
