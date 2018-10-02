# pylint: disable=protected-access, C0413, W0611, C0301
import os
import sys
from pathlib import Path
import unittest
import PIL.Image
sys.path.insert(0, os.getcwd())
from video_and_photo_tools.image_cache import ImageCache
import video_and_photo_tools.pil_image_extensions

class TestImageCache(unittest.TestCase):

    TEST_IMAGE_PATH = Path('.') / 'data/test_data/test_images/photo.jpg'
    IMAGE_CACHE_DIR_PATH = Path('.') / 'data/test_data/test_cache'

    def setUp(self):
        self.image_cache = ImageCache(cache_dir_path=TestImageCache.IMAGE_CACHE_DIR_PATH)
        self.image = PIL.Image.open(TestImageCache.TEST_IMAGE_PATH)
        self.width = 640
        self.image_rgb_640 = self.image.resize_with_width_preserve_aspect(self.width)
        self.image_l_640 = self.image_rgb_640.convert('L')
        self.video_id = 'test_video_id'
        self.frame_num = 500

    def test_setup(self):
        self.assertEqual(self.image_l_640.mode, 'L')
        self.assertEqual(self.image_rgb_640.mode, 'RGB')

    def test_destroy_cache_dir(self):
        self.image_cache._ensure_cache_dir()
        for suffix in ImageCache.VALID_SUFFIXES:
            (TestImageCache.IMAGE_CACHE_DIR_PATH / ('foo.' + suffix)).touch()

        self.assertTrue(os.path.isdir(TestImageCache.IMAGE_CACHE_DIR_PATH))

        for suffix in ImageCache.VALID_SUFFIXES:
            self.assertTrue(os.path.isfile(TestImageCache.IMAGE_CACHE_DIR_PATH / ('foo.' + suffix)))

        self.image_cache.destroy_cache_dir()
        self.assertFalse(os.path.isdir(TestImageCache.IMAGE_CACHE_DIR_PATH))

    def test_store(self):
        self.store_images()

    def store_images(self):
        self.image_cache.clear_cache()
        for suffix in ImageCache.VALID_SUFFIXES:
            self.assertEqual(0, len(list(TestImageCache.IMAGE_CACHE_DIR_PATH.glob('*.' + suffix))))

        for suffix in ImageCache.VALID_SUFFIXES:
            for image in [self.image_rgb_640, self.image_l_640]:
                self.image_cache.store(self.video_id, image, self.frame_num, suffix)
            self.assertEqual(2, len(list(TestImageCache.IMAGE_CACHE_DIR_PATH.glob('*.' + suffix))))

    def test_fetch(self):
        self.image_cache.clear_cache()

        for image_format in ImageCache.VALID_SUFFIXES:
            for mode in ['RGB', 'L']:
                fetched = self.image_cache.fetch(self.video_id,
                                                 self.width,
                                                 mode,
                                                 self.frame_num,
                                                 image_format)
                self.assertIsNone(fetched)

        self.store_images()

        for image_format in ImageCache.VALID_SUFFIXES:
            for mode in ['RGB', 'L']:
                fetched = self.image_cache.fetch(self.video_id,
                                                 self.width,
                                                 mode,
                                                 self.frame_num,
                                                 image_format)
                self.assertIsNotNone(fetched)


if __name__ == '__main__':
    unittest.main()
