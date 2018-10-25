# pylint: disable=C0413, W0212
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.fov_time_base_aligner import FovTimebaseAligner
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper as LDFH
from video_and_photo_tools.image_from_video import ImageFromVideo

class TestPanMoterTimebaseAligner(unittest.TestCase):

    HEAD_PATH = Path('/Volumes/WD')
    TEST_SESSION_DIR_NAME = 'Aug_17_Palo_Alto_High_2nd_time_B80_ottofillmore'

    def setUp(self):
        self.ldfh = LDFH(self.__class__.HEAD_PATH)
        self.fovta = FovTimebaseAligner(self.__class__.TEST_SESSION_DIR_NAME)

    def dont_test_visualize(self):
        self.fovta.visualize()

    def dont_test_unique_transitions(self):
        u = self.fovta.get_unique_transitions()

    def test_run(self):
        self.fovta.run()

if __name__ == '__main__':
    unittest.main()