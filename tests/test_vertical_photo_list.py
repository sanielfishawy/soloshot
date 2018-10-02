import sys
import os
import unittest
from pathlib import Path
import PIL
import PIL.Image

sys.path.insert(0, os.getcwd())
from tk_canvas_renderers.vertical_photo_list import VerticalPhotoList

class TestVerticalPhotoList(unittest.TestCase):

    TEST_PHOTO_FILE_PATH = Path('.') / 'data/test_data/test_images/photo.jpg'

    def setUp(self):
        self.photos = [PIL.Image.open(TestVerticalPhotoList.TEST_PHOTO_FILE_PATH) for _ in range(5)]
        self.photo_renderer = VerticalPhotoList(self.photos, num_photos_displayed_vertically=1)

    def dont_test_get_resized_photos(self):
        self.photo_renderer._setup_ui()
        for photo in self.photo_renderer._get_resized_photos():
            self.assertIsInstance(photo, PIL.Image.Image)
            self.assertGreater(photo.width, 0)
            self.assertGreater(photo.height, 0)
            self.assertLess(photo.width, self.photos[0].width)

    def test_visualize(self):
        self.photo_renderer.run()

if __name__ == '__main__':
    unittest.main()