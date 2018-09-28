import sys
import os
import unittest
from pathlib import Path
sys.path.insert(0, os.getcwd())

from tk_canvas_renderers.still_picker import StillPicker
from video_and_photo_tools.video_helper import VideoHelper

class TestStillPicker(unittest.TestCase):

    TEST_VIDEO_PATH = Path('.') / 'data/test_data/test_videos/video.mp4'

    def setUp(self):
        self.video_helper = VideoHelper(TestStillPicker.TEST_VIDEO_PATH)
        middle_frame = int(self.video_helper.get_frame_count() / 2)
        self.images_from_video = self.video_helper.get_images_around_frame_number(middle_frame, 50, 50)
        self.still_picker = StillPicker(self.images_from_video,
                                        selector_type=StillPicker.SELECT_SINGLE_IMAGE,
                                       )

    def test_foo(self):
        self.still_picker.run()

if __name__ == '__main__':
    unittest.main()
