# pylint: disable=C0413
import sys
import os
import unittest
from pathlib import Path
import tkinter as tk
import numpy as np

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.tag_postion_in_stable_fov_segments_analyzer import TagPositionInStableFovSegmentsAnalyzer
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper
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

    def test_visualize_mean_base_latitude(self):
        geo_map_scrubber = GeoMapScrubber(
            latitude_series=self.tag_latitude_series,
            longitude_series=self.tag_longitude_series,
            time_series=self.tag_time_series,
        )

        master = tk.Tk()
        geo_map_scrubber.setup_ui(master)

        mean_base_latitude = np.mean(self.base_latitude_series)
        mean_base_longitude = np.mean(self.base_longitude_series)
        geo_map_scrubber.add_marker(
            latitude=mean_base_latitude,
            longitude=mean_base_longitude,
            text='mean_base_position',
        )
        master.mainloop()

if __name__ == '__main__':
    unittest.main()
