# pylint: disable=C0413
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.pan_motor_timebase_aligner import PanMotorTimeBaseAligner
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper as LDFH
from video_and_photo_tools.image_from_video import ImageFromVideo

class TestPanMoterTimebaseAligner(unittest.TestCase):

    HEAD_PATH = Path('/Volumes/WD')
    TEST_SESSION_DIR_NAME = 'Aug_17_Palo_Alto_High_2nd_time_B80_ottofillmore'

    def setUp(self):
        self.ldfh = LDFH(self.__class__.HEAD_PATH)
        self.pmta = PanMotorTimeBaseAligner(self.__class__.TEST_SESSION_DIR_NAME)

    def dont_test_visualize_peaks(self):
        self.pmta.visualize_motor_local_maxima_and_minima()

    def dont_test_show_scrubber_for_maxima(self):
        self.pmta.show_scrub_picker_for_maxima()

    def dont_test_show_scrubber_for_minima(self):
        self.pmta.show_scrub_picker_for_minima()

    def dont_test_get_images_around_time(self):
        times = self.pmta.get_time_at_maxima()
        images_around_times = [self.pmta.get_images_around_time(time)
                               for time in times]
        for images in images_around_times:
            for image in images:
                self.assertIsInstance(image, ImageFromVideo)

    def test_run(self):
        self.pmta.show_scrub_picker_for_min_and_max()
        self.pmta.log_data()

if __name__ == '__main__':
    unittest.main()
