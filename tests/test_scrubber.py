# pylint: disable=C0301, C0413, W0221
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

    def setUp(self, selector_type=ScrubPicker.SELECT_RANGE):
        self.image_from_video_grabber = ImageFromVideoGrabber(TestScrubber.TEST_VIDEO_PATH,
                                                              cache_dir_path=TestScrubber.IMAGE_CACHE_DIR_PATH)

        middle_frame = int(self.image_from_video_grabber.get_frame_count() / 2)
        self.images_from_video = self.image_from_video_grabber.get_images_around_frame_number(middle_frame, 100, 100)

        self.scrub_picker = ScrubPicker(images_from_video=self.images_from_video,
                                        selector_type=selector_type,
                                        callback=self.callback,
                                       )

        return self

    def visualize(self):
        self.scrub_picker.run()

    def callback(self, images):
        print(images)

if __name__ == '__main__':
    unittest.main()
