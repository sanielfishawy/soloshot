# pylint: disable=C0301, C0413
import sys
import os
import unittest
from pathlib import Path
sys.path.insert(0, os.getcwd())
from tk_canvas_renderers.scrub_picker import ScrubPicker
from video_and_photo_tools.image_from_video_grabber import ImageFromVideoGrabber


class TestScrubber(unittest.TestCase):

    TEST_VIDEO_PATH = Path('.') / 'data/test_data/test_videos/video.mp4'
    IMAGE_CACHE_DIR_PATH = Path('.') / 'data/test_data/test_cache'

    def setUp(self):
        self.image_from_video_grabber = ImageFromVideoGrabber(TestScrubber.TEST_VIDEO_PATH,
                                                              cache_dir_path=TestScrubber.IMAGE_CACHE_DIR_PATH)

        middle_frame = int(self.image_from_video_grabber.get_frame_count() / 2)
        self.images_from_video = self.image_from_video_grabber.get_images_around_frame_number(middle_frame, 10, 10)

        self.scrub_picker = ScrubPicker(images_from_video=self.images_from_video,
                                        selector_type=ScrubPicker.SELECT_RANGE,
                                       )

    def test_visualize(self):
        self.scrub_picker.run()

if __name__ == '__main__':
    unittest.main()
