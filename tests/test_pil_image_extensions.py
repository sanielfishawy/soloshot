# pylint: disable=C0413, W0611
import sys
import os
import unittest
from pathlib import Path
import PIL.Image

sys.path.insert(0, os.getcwd())
import video_and_photo_tools.pil_image_extensions

class TestImageExtension(unittest.TestCase):

    IMAGE_PATH = Path('.') / 'data/test_data/test_images/photo.jpg'

    def setUp(self):
        self.image = PIL.Image.open(TestImageExtension.IMAGE_PATH)
        self.aspect = self.image.get_aspect()

    def test_resize_with_height(self):
        self.assertGreater(self.image.height, 480)
        resized = self.image.resize_with_height_preserve_aspect(480)
        self.assertEqual(resized.height, 480)
        self.assertEqual(resized.get_aspect(), self.aspect)

    def test_resize_with_width(self):
        self.assertGreater(self.image.width, 640)
        resized = self.image.resize_with_width_preserve_aspect(640)
        self.assertEqual(resized.width, 640)
        self.assertEqual(resized.get_aspect(), self.aspect)

    def test_get_aspect(self):
        self.assertEqual(self.aspect, self.image.width / self.image.height)


if __name__ == '__main__':
    unittest.main()
