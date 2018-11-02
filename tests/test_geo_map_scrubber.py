# pylint: disable=C0413
import sys
import os
from pathlib import Path
import unittest

sys.path.insert(0, os.getcwd())
from tk_canvas_renderers.geo_map_scrubber import GeoMapScrubber
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper

class TestGeoMapScrubber(unittest.TestCase):

    HEAD_PATH = Path('/Volumes/WD')
    SESSION_DIR_NAME = 'Aug_17_Palo_Alto_High_2nd_time_B80_ottofillmore'

    def setUp(self):
        ldfh = LegacyDataFileSystemHelper(self.__class__.HEAD_PATH)
        self.latitude_series = ldfh.get_field_from_npz_file(
            self.__class__.SESSION_DIR_NAME,
            LegacyDataFileSystemHelper.TAG_NPZ_FILE,
            LegacyDataFileSystemHelper.TAG_LATITUDE_FIELD,
        )
        self.longitude_series = ldfh.get_field_from_npz_file(
            self.__class__.SESSION_DIR_NAME,
            LegacyDataFileSystemHelper.TAG_NPZ_FILE,
            LegacyDataFileSystemHelper.TAG_LONGITUDE_FIELD,
        )
        return self

    def visualize(self):
        GeoMapScrubber(
            self.latitude_series,
            self.longitude_series,
            height=800,
        ).run()


if __name__ == '__main__':
    unittest.main()
