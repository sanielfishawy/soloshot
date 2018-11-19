# pylint: disable=C0301, C0413, W0212
import os
import sys
import unittest
from pathlib import Path
import PIL.Image
import cv2

sys.path.insert(0, os.getcwd())
from video_and_photo_tools.image_from_video_grabber import ImageFromVideoGrabber

class TestImageFromVideoGrabber(unittest.TestCase):

    TEST_VIDEO_PATH = Path('.') / 'data/test_data/test_videos/video.mp4'
    TEST_CACHE_DIR_PATH = Path('.') / 'data/test_data/test_cache'

    def setUp(self):
        self.image_from_video_grabber = ImageFromVideoGrabber(TestImageFromVideoGrabber.TEST_VIDEO_PATH,
                                        cache_dir_path=TestImageFromVideoGrabber.TEST_CACHE_DIR_PATH)
        self.image_from_video_grabber._image_cache.clear_cache()
        self.cap = cv2.VideoCapture(str(TestImageFromVideoGrabber.TEST_VIDEO_PATH.resolve()))
        self.video_duration_ms = self.image_from_video_grabber.get_video_duration_ms()
        self.mid_frame = int(self.image_from_video_grabber.get_frame_count() / 2)
        self.mid_time_ms = self.image_from_video_grabber.get_time_ms_for_frame_num(self.mid_frame)

    def test_get_video_id(self):
        size = str(os.path.getsize(TestImageFromVideoGrabber.TEST_VIDEO_PATH))
        filename = TestImageFromVideoGrabber.TEST_VIDEO_PATH.name
        self.assertEqual(self.image_from_video_grabber.get_video_id(), filename + '-' + size)

    def test_get_image_at_frame_saves_and_retrieves_from_cache(self):
        self.image_from_video_grabber._image_cache.clear_cache()
        self.assertEqual(0, len(list(TestImageFromVideoGrabber.TEST_CACHE_DIR_PATH.glob('*'))))
        img = self.image_from_video_grabber.get_image_at_frame_num(self.mid_frame)
        self.assertEqual(1, len(list(TestImageFromVideoGrabber.TEST_CACHE_DIR_PATH.glob('*'))))
        self.assertFalse(img.get_from_cache())
        img = self.image_from_video_grabber.get_image_at_frame_num(self.mid_frame)
        self.assertTrue(img.get_from_cache())

    def test_time_ms_field_in_returned_image_is_correct(self):
        self.image_from_video_grabber._image_cache.clear_cache()
        img = self.image_from_video_grabber.get_image_at_frame_num(self.mid_frame)
        self.assertEqual(int(self.mid_time_ms), img.get_time_ms())
        img = self.image_from_video_grabber.get_image_at_frame_num(self.mid_frame)
        self.assertAlmostEqual(int(self.mid_time_ms), img.get_time_ms())
        self.assertTrue(img.get_from_cache())

    def test_returns_image_with_correct_width_and_mode(self):
        self.image_from_video_grabber._image_cache.clear_cache()
        img = self.image_from_video_grabber.get_image_at_frame_num(self.mid_frame)
        self.assertEqual(img.get_image().width, self.image_from_video_grabber._image_width)
        self.assertEqual(img.get_image().mode, self.image_from_video_grabber._image_mode)

    def test_get_image_from_video_at_frame_returns_the_correct_data(self):
        frame_num = int(self.image_from_video_grabber.get_frame_count() / 2)
        img = self.image_from_video_grabber.get_image_at_frame_num(frame_num)
        self.assertIsInstance(img.get_image(), PIL.Image.Image)
        self.assertEqual(img.get_frame_num(), frame_num)
        self.assertEqual(img.get_time_ms(), int(self.image_from_video_grabber.get_time_ms_for_frame_num(frame_num)))

    def test_get_image_from_video_at_frame_after_end_returns_last(self):
        frame_num = self.image_from_video_grabber.get_frame_count()
        img = self.image_from_video_grabber.get_image_at_frame_num(frame_num)
        self.assertEqual(img.get_frame_num(), self.image_from_video_grabber.get_frame_count() - 1)

    def test_bounded_frame_number_gives_last_retrievable_frame_num_for_inputs_greater_than_frame_count(self):
        for plus_n in range(3):
            frame_count = self.image_from_video_grabber.get_frame_count() + plus_n
            last_retrievable_frame_num = self.image_from_video_grabber.get_frame_count() - 1
            self.assertEqual(last_retrievable_frame_num,
                             self.image_from_video_grabber.bounded_frame_num(frame_count))

    def test_get_n_gets_the_right_frames(self):
        num = 20
        last_num = self.mid_frame + num - 1

        ifvs = self.image_from_video_grabber.get_num_images_from_video_after_start_n(self.mid_frame, num)
        self.assertEqual(len(ifvs), num)
        for idx, ivf in enumerate(ifvs):
            self.assertEqual(ivf.get_frame_num(), self.mid_frame + idx)

        last = ifvs[-1]
        direct_last = self.image_from_video_grabber.get_image_at_frame_num(last_num)
        self.assertEqual(last.get_frame_num(), direct_last.get_frame_num())
        self.assertAlmostEqual(last.get_time_ms(), direct_last.get_time_ms())

    def test_get_n_retrieves_from_cache(self):
        self.image_from_video_grabber._image_cache.clear_cache()
        num = 20
        ifvs = self.image_from_video_grabber.get_num_images_from_video_after_start_n(self.mid_frame, num)
        self.assertEqual(len(ifvs), num)
        for ifv in ifvs:
            self.assertFalse(ifv.get_from_cache())

        ifvs = self.image_from_video_grabber.get_num_images_from_video_after_start_n(self.mid_frame, num)
        self.assertEqual(len(ifvs), num)
        for ifv in ifvs:
            self.assertTrue(ifv.get_from_cache())

        del_from_cache_frame_num = self.mid_frame + 5
        del_from_cache_file = TestImageFromVideoGrabber.TEST_CACHE_DIR_PATH / f'video.mp4-3725381013-width=640-mode=L-frame_num={del_from_cache_frame_num}.jpg'
        os.remove(del_from_cache_file.resolve())

        ifvs = self.image_from_video_grabber.get_num_images_from_video_after_start_n(self.mid_frame, num)
        for ifv in ifvs:
            if ifv.get_frame_num() == del_from_cache_frame_num:
                self.assertFalse(ifv.get_from_cache())
            else:
                self.assertTrue(ifv.get_from_cache())


if __name__ == '__main__':
    unittest.main()
