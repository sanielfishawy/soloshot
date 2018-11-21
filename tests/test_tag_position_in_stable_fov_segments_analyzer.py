# pylint: disable=C0413, W0212, C0301
import sys
import os
import unittest
from pathlib import Path
import tkinter as tk
import numpy as np

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.tag_postion_in_stable_fov_segments_analyzer import TagPositionInStableFovSegmentsAnalyzer
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper as LDFH
from legacy_data_pipeline.stable_fov_segmenter import StableFovSegmenter
from tk_canvas_renderers.geo_map_scrubber import GeoMapScrubber
from tag import Tag
from base import Base

class TestTagPositionInStableFovSegmentAnalyzer(unittest.TestCase):


    def setUp(self):
        head_path = Path('/Volumes/WD')
        session_dir = 'Aug_17_Palo_Alto_High_2nd_time_B80_ottofillmore'

        ldfh = LDFH(head_path)

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
        self.tag_time_series = ldfh.get_field_from_npz_file(
            session_dir_name=session_dir,
            filename=LDFH.TAG_NPZ_FILE,
            fieldname=LDFH.TAG_TIME_FIELD,
        )

        self.geo_map_scrubber = GeoMapScrubber(
            latitude_series=tag_latitude_series,
            longitude_series=tag_longitude_series,
            time_series=self.tag_time_series,
        )

        tag = Tag(
            latitude_series=tag_latitude_series,
            longitude_series=tag_longitude_series,
            time_series=self.tag_time_series,
            map_coordinate_transformer=self.geo_map_scrubber._get_map_coordinate_transformer(),
        )

        self.base_latitude_series = ldfh.get_field_from_npz_file(
            session_dir_name=session_dir,
            filename=LDFH.TAG_NPZ_FILE,
            fieldname=LDFH.BASE_LATITUDE_FIELD,
        )
        self.base_longitude_series = ldfh.get_field_from_npz_file(
            session_dir_name=session_dir,
            filename=LDFH.TAG_NPZ_FILE,
            fieldname=LDFH.BASE_LONGITUDE_FIELD,
        )

        reported_base = Base(
            gps_latitude_series=self.base_latitude_series,
            gps_longitude_series=self.base_longitude_series,
            map_coordinate_transformer=self.geo_map_scrubber._get_map_coordinate_transformer(),
        )

        # Base position we believe to be correct based on where we believe we set up
        # the base on the field. Point picked on map using GeoMapScrubber
        # x: 132 y: 612 latitude: 37.38639419602273 longitude: -122.11008779357967
        actual_base_latitude_series = np.full(self.base_latitude_series.size, 37.38639419602273)
        actual_base_longitude_series = np.full(self.base_longitude_series.size, -122.11008779357967)

        actual_base = Base(
            gps_latitude_series=actual_base_latitude_series,
            gps_longitude_series=actual_base_longitude_series,
            map_coordinate_transformer=self.geo_map_scrubber._get_map_coordinate_transformer(),
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

        self.tag_position_analyzer_with_actual_base = TagPositionInStableFovSegmentsAnalyzer(
            fov_series=fov_series,
            fov_time_series=fov_time_series,
            tag=tag,
            base=actual_base,
        )

        self.tag_position_analyzer_with_reported_base = TagPositionInStableFovSegmentsAnalyzer(
            fov_series=fov_series,
            fov_time_series=fov_time_series,
            tag=tag,
            base=reported_base,
        )

    def dont_test_get_tag_idxs_for_stable_segment(self):
        segments = self.tag_position_analyzer_with_actual_base._get_stable_fov_segments()
        tag_idxs = self.tag_position_analyzer_with_actual_base._get_tag_idxs_for_stable_segments()
        num_not_too_short_segments = len([
            segment for segment in segments
            if not StableFovSegmenter.segment_is_too_short(segment)
        ])
        self.assertEqual(
            num_not_too_short_segments,
            len(tag_idxs),
        )

    def test_visualize_tag_positions(self):
        limit = 3
        frames = self.tag_position_analyzer_with_reported_base.get_frames_in_stable_fovs(
            angle_threshold_rad=np.radians(10),
            limit=limit,
        )

        master = tk.Tk()
        self.geo_map_scrubber.setup_ui(master)

        for frame in frames:
            early_x_y_pos = self.tag_position_analyzer_with_actual_base.get_early_position(frame)
            late_x_y_pos = self.tag_position_analyzer_with_actual_base.get_late_position(frame)

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
