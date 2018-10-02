# pylint: disable=C0301, C0413, W0212
import os
import sys
import unittest
from pathlib import Path
import PIL.Image
import cv2
sys.path.insert(0, os.getcwd())
from video_and_photo_tools.video_helper import VideoHelper

class TestVideoHelper(unittest.TestCase):

    TEST_VIDEO_PATH = Path('.') / 'data/test_data/test_videos/video.mp4'
    TEST_CACHE_DIR_PATH = Path('.') / 'data/test_data/test_cache'

    def setUp(self):
        self.video_helper = VideoHelper(TestVideoHelper.TEST_VIDEO_PATH,
                                        cache_dir_path=TestVideoHelper.TEST_CACHE_DIR_PATH)
        self.video_helper._image_cache.clear_cache()
        self.cap = cv2.VideoCapture(str(TestVideoHelper.TEST_VIDEO_PATH.resolve()))
        self.video_duration_ms = self.video_helper.get_video_duration_ms()
        self.mid_frame = (self.video_helper.get_frame_count() / 2)
        self.mid_time_ms = self.video_helper.get_time_ms_for_frame_num(self.mid_frame)

    def test_get_video_id(self):
        size = str(os.path.getsize(TestVideoHelper.TEST_VIDEO_PATH))
        filename = TestVideoHelper.TEST_VIDEO_PATH.name
        self.assertEqual(self.video_helper.get_video_id(), filename + '-' + size)

    def test_get_image_at_frame_saves_and_retrieves_from_cache(self):
        self.video_helper._image_cache.clear_cache()
        self.assertEqual(0, len(list(TestVideoHelper.TEST_CACHE_DIR_PATH.glob('*'))))
        img = self.video_helper.get_image_at_frame_num(self.mid_frame)
        self.assertEqual(1, len(list(TestVideoHelper.TEST_CACHE_DIR_PATH.glob('*'))))
        self.assertFalse(img.get_from_cache())
        img = self.video_helper.get_image_at_frame_num(self.mid_frame)
        self.assertTrue(img.get_from_cache())

    def test_time_ms_field_in_returned_image_is_correct(self):
        self.video_helper._image_cache.clear_cache()
        img = self.video_helper.get_image_at_frame_num(self.mid_frame)
        self.assertEqual(self.mid_time_ms, img.get_time_ms())
        img = self.video_helper.get_image_at_frame_num(self.mid_frame)
        self.assertEqual(self.mid_time_ms, img.get_time_ms())
        self.assertTrue(img.get_from_cache())

    def test_returns_image_with_correct_width_and_mode(self):
        self.video_helper._image_cache.clear_cache()
        img = self.video_helper.get_image_at_frame_num(self.mid_frame)
        self.assertEqual(img.get_image().width, self.video_helper._image_width)
        self.assertEqual(img.get_image().mode, self.video_helper._image_mode)

    def test_get_image_from_video_at_frame_returns_the_correct_data(self):
        frame_num = int(self.video_helper.get_frame_count() / 2)
        img = self.video_helper.get_image_at_frame_num(frame_num)
        self.assertIsInstance(img.get_image(), PIL.Image.Image)
        self.assertEqual(img.get_frame_num(), frame_num)
        self.assertEqual(img.get_time_ms(), self.video_helper.get_time_ms_for_frame_num(frame_num))

    def test_get_image_from_video_at_frame_after_end_returns_last(self):
        frame_num = self.video_helper.get_frame_count()
        img = self.video_helper.get_image_at_frame_num(frame_num)
        self.assertEqual(img.get_frame_num(), self.video_helper.get_frame_count() - 1)

    def test_bounded_frame_number_gives_last_retrievable_frame_num_for_inputs_greater_than_frame_count(self):
        for plus_n in range(3):
            frame_count = self.video_helper.get_frame_count() + plus_n
            last_retrievable_frame_num = self.video_helper.get_frame_count() - 1
            self.assertEqual(last_retrievable_frame_num,
                             self.video_helper.bounded_frame_num(frame_count))

    def test_get_n_gets_the_right_frames(self):
        mid_num = int(self.video_helper.get_frame_count() / 2)
        num = 20
        last_num = mid_num + num - 1

        ifvs = self.video_helper.get_num_images_from_after_start_n(mid_num, num)
        self.assertEqual(len(ifvs), num)
        for idx, ivf in enumerate(ifvs):
            self.assertEqual(ivf.get_frame_num(), int(mid_num) + idx)

        last = ifvs[-1]
        direct_last = self.video_helper.get_image_at_frame_num(last_num)
        self.assertEqual(last.get_frame_num(), direct_last.get_frame_num())
        self.assertAlmostEqual(last.get_time_ms(), direct_last.get_time_ms())

    def dont_test_performance_of_grabbing_100_frames(self):
        mid = self.video_helper.get_video_duration_ms() / 2
        self.video_helper.get_images_around_time_ms(mid, 5, 5)

    def dont_test_performance_of_open_cv_read(self):
        mid = self.video_helper.get_frame_count() / 2
        for n in range(100):
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, mid + n)
            success, arr = self.cap.read()
            self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()
