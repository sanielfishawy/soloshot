# pylint: disable=C0413, W0212
import sys
import os
import unittest
from pathlib import Path
import tkinter as tk
import numpy as np

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.tag_postion_in_stable_fov_segments_analyzer import TagPositionInStableFovSegmentsAnalyzer
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper
from legacy_data_pipeline.stable_fov_segmenter import StableFovSegmenter
from geo_mapping.geo_mapper import MapCoordinateTransformer
from tk_canvas_renderers.geo_map_scrubber import GeoMapScrubber
from tag import Tag
from base import Base

class TestTagPositionInStableFovSegmentAnalyzer(unittest.TestCase):

    HEAD_PATH = Path('/Volumes/WD')
    SESSION_DIR = 'Aug_17_Palo_Alto_High_2nd_time_B80_ottofillmore'

    def setUp(self):
        ldfh = LegacyDataFileSystemHelper(self.__class__.HEAD_PATH)
        self.tag_latitude_series = ldfh.get_field_from_npz_file(
            session_dir_name=self.__class__.SESSION_DIR,
            filename=LegacyDataFileSystemHelper.TAG_NPZ_FILE,
            fieldname=LegacyDataFileSystemHelper.TAG_LATITUDE_FIELD,
        )
        self.tag_longitude_series = ldfh.get_field_from_npz_file(
            session_dir_name=self.__class__.SESSION_DIR,
            filename=LegacyDataFileSystemHelper.TAG_NPZ_FILE,
            fieldname=LegacyDataFileSystemHelper.TAG_LONGITUDE_FIELD,
        )
        self.tag_time_series = ldfh.get_field_from_npz_file(
            session_dir_name=self.__class__.SESSION_DIR,
            filename=LegacyDataFileSystemHelper.TAG_NPZ_FILE,
            fieldname=LegacyDataFileSystemHelper.TAG_TIME_FIELD,
        )

        self.geo_map_scrubber = GeoMapScrubber(
            latitude_series=self.tag_latitude_series,
            longitude_series=self.tag_longitude_series,
            time_series=self.tag_time_series,
        )

        self.tag = Tag(
            latitude_series=self.tag_latitude_series,
            longitude_series=self.tag_longitude_series,
            time_series=self.tag_time_series,
            map_coordinate_transformer=self.geo_map_scrubber._get_map_coordinate_transformer(),
        )

        self.base_latitude_series = ldfh.get_field_from_npz_file(
            session_dir_name=self.__class__.SESSION_DIR,
            filename=LegacyDataFileSystemHelper.TAG_NPZ_FILE,
            fieldname=LegacyDataFileSystemHelper.BASE_LATITUDE_FIELD,
        )
        self.base_longitude_series = ldfh.get_field_from_npz_file(
            session_dir_name=self.__class__.SESSION_DIR,
            filename=LegacyDataFileSystemHelper.TAG_NPZ_FILE,
            fieldname=LegacyDataFileSystemHelper.BASE_LONGITUDE_FIELD,
        )

        # Base position we believe to be correct based on where we believe we set up
        # the base on the field. Point picked on map using GeoMapScrubber
        # x: 132 y: 612 latitude: 37.38639419602273 longitude: -122.11008779357967
        self.actual_base_latitude = 37.38639419602273
        self.actual_base_longitude = -122.11008779357967

        self.actual_base = Base(
            gps_latitude=self.actual_base_latitude,
            gps_longitude=self.actual_base_longitude,
            map_coordinate_transformer=self.geo_map_scrubber._get_map_coordinate_transformer(),
        )

        self.fov_series = ldfh.get_field_from_npz_file(
            session_dir_name=self.__class__.SESSION_DIR,
            filename=LegacyDataFileSystemHelper.LENS_NPZ_FILE,
            fieldname=LegacyDataFileSystemHelper.LENS_FOV_FIELD,
        )
        self.fov_time_series = ldfh.get_field_from_npz_file(
            session_dir_name=self.__class__.SESSION_DIR,
            filename=LegacyDataFileSystemHelper.LENS_NPZ_FILE,
            fieldname=LegacyDataFileSystemHelper.LENS_TIME_FIELD,
        )

        self.tag_position_analyzer = TagPositionInStableFovSegmentsAnalyzer(
            fov_series=self.fov_series,
            fov_time_series=self.fov_time_series,
            tag=self.tag,
            base=self.actual_base,
        )

    def test_get_tag_idxs_for_stable_segment(self):
        segments = self.tag_position_analyzer._get_stable_fov_segments()
        tag_idxs = self.tag_position_analyzer._get_tag_idxs_for_stable_segments()
        num_not_too_short_segments = len([
            segment for segment in segments
            if not StableFovSegmenter.segment_is_too_short(segment)
        ])
        self.assertEqual(
            num_not_too_short_segments,
            len(tag_idxs),
        )

    def dont_test_visualize_tag_positions(self):
        frames = self.tag_position_analyzer.get_frames_in_stable_fovs(np.radians(10))

        master = tk.Tk()
        self.geo_map_scrubber.setup_ui(master)

        for frame in frames:
            early_x_y_pos = self.tag_position_analyzer.get_early_position(frame)
            late_x_y_pos = self.tag_position_analyzer.get_late_position(frame)

            self.geo_map_scrubber.add_marker_x_y(*early_x_y_pos)
            self.geo_map_scrubber.add_marker_x_y(*late_x_y_pos)

        master.mainloop()


    def dont_test_visualize_base_track(self):
        GeoMapScrubber(
            latitude_series=self.base_latitude_series,
            longitude_series=self.base_longitude_series,
            time_series=self.tag_time_series,
            border_feet=50,
        ).run()

    def dont_test_visualize_mean_base_position(self):
        master = tk.Tk()
        self.geo_map_scrubber.setup_ui(master)

        mean_base_latitude = np.mean(self.base_latitude_series)
        mean_base_longitude = np.mean(self.base_longitude_series)
        self.geo_map_scrubber.add_marker_lat_long(
            latitude=mean_base_latitude,
            longitude=mean_base_longitude,
            text='mean_base_position',
        )
        master.mainloop()

if __name__ == '__main__':
    unittest.main()
