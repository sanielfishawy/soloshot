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

    def setUp(self):
        self.video_helper = VideoHelper(TestVideoHelper.TEST_VIDEO_PATH)
        self.cap = cv2.VideoCapture(str(TestVideoHelper.TEST_VIDEO_PATH.resolve()))
        self.video_duration_ms = self.video_helper.get_video_duration_ms()

    def test_get_video_id(self):
        size = str(os.path.getsize(TestVideoHelper.TEST_VIDEO_PATH))
        filename = TestVideoHelper.TEST_VIDEO_PATH.name
        self.assertEqual(self.video_helper.get_video_id(), filename + '-' + size)

    def test_get_image_from_video_at_frame_returns_the_correct_data(self):
        frame_num = int(self.video_helper.get_frame_count() / 2)
        im = self.video_helper.get_image_from_video_at_frame_num(frame_num)
        self.assertIsInstance(im.get_image(), PIL.Image.Image)
        self.assertEqual(im.get_frame_num(), frame_num)
        self.assertEqual(im.get_time_ms(), self.video_helper.get_time_ms_for_frame_num(frame_num))

    def test_get_image_from_video_at_frame_after_end_returns_last(self):
        frame_num = self.video_helper.get_frame_count()
        im = self.video_helper.get_image_from_video_at_frame_num(frame_num)
        self.assertEqual(im.get_frame_num(), self.video_helper.get_frame_count() - 1)

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
        direct_last = self.video_helper.get_image_from_video_at_frame_num(last_num)
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
