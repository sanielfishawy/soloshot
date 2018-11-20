# pylint: disable=C0413
import sys
import os
import unittest
from pathlib import Path
import math

sys.path.insert(0, os.getcwd())
from video_and_photo_tools.image_from_video_grabber import ImageFromVideoGrabber
from legacy_data_pipeline.manual_visual_angle_calculator import ManualVisualAngleCalculator

class TestManualVisualAngleCalculator(unittest.TestCase):

    TEST_VIDEO_PATH = Path('.') / 'data/test_data/test_videos/video.mp4'
    TEST_CACHE_DIR_PATH = Path('.') / 'data/test_data/test_cache'

    def setUp(self):
        image_from_video_grabber = ImageFromVideoGrabber(
            self.__class__.TEST_VIDEO_PATH,
            cache_dir_path=self.__class__.TEST_CACHE_DIR_PATH
        )

        middle_frame = int(image_from_video_grabber.get_frame_count() / 2)
        images_from_video = image_from_video_grabber.get_num_images_from_video_after_start_n(
            middle_frame,
            100,
        )
        self.mvac = ManualVisualAngleCalculator(
            image_from_video_1=images_from_video[0],
            image_from_video_2=images_from_video[-1],
            fov_rad=math.pi/2,
            callback=self._vac_callback,
        )

    def test_run(self):
        self.mvac.run()

    def _vac_callback(self, angle_data):
        print(angle_data)

if __name__ == '__main__':
    unittest.main()
