# pylint: disable=C0301, C0413, W0212
import sys
import os
import unittest
from pathlib import Path

sys.path.insert(0, os.getcwd())
from tk_canvas_renderers.vertical_photo_list import VerticalPhotoList
from video_and_photo_tools.image_from_video_grabber import ImageFromVideoGrabber


class TestVerticalPhotoList(unittest.TestCase):

    TEST_VIDEO_PATH = Path('.') / 'data/test_data/test_videos/video.mp4'
    TEST_CACHE_DIR_PATH = Path('.') / 'data/test_data/test_cache'

    def setUp(self):
        self.image_from_video_grabber = ImageFromVideoGrabber(TestVerticalPhotoList.TEST_VIDEO_PATH,
                                                              cache_dir_path=TestVerticalPhotoList.TEST_CACHE_DIR_PATH)

        middle_frame = int(self.image_from_video_grabber.get_frame_count() / 2)
        self.images_from_video = self.image_from_video_grabber.get_num_images_from_video_after_start_n(middle_frame, 5)
        self.vertical_photo_list = VerticalPhotoList(self.images_from_video)

    def test_visualize(self):
        self.vertical_photo_list.run()

if __name__ == '__main__':
    unittest.main()
