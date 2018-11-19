# pylint: disable=C0301, C0413, W0221
import sys
import os
import unittest
from pathlib import Path

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper
from tk_canvas_renderers.video_plus_map_scrub_picker import VideoPlusMapScrubPicker
from tk_canvas_renderers.scrub_picker import ScrubPicker
from tk_canvas_renderers.geo_map_scrubber import GeoMapScrubber
from video_and_photo_tools.image_from_video_grabber import ImageFromVideoGrabber

class TestVideoPlusMapScrubber(unittest.TestCase):

    INPUT_DATA_HEAD_PATH = Path('/Volumes/WD')
    SESSION_DIR = 'Aug_17_Palo_Alto_High_2nd_time_B80_ottofillmore'
    IMAGE_CACHE_DIR_PATH = Path('/Volumes/WD/image_cache')

    def setUp(self):
        ldfh = LegacyDataFileSystemHelper(self.__class__.INPUT_DATA_HEAD_PATH)
        image_from_video_grabber = ImageFromVideoGrabber(
            ldfh.get_video_path(self.__class__.SESSION_DIR),
            cache_dir_path=self.__class__.IMAGE_CACHE_DIR_PATH,
        )

        middle_frame = int(image_from_video_grabber.get_frame_count() / 2)
        images_from_video = image_from_video_grabber.get_images_around_frame_number(middle_frame, 100, 100)
        video_scrub_picker = ScrubPicker(
            images_from_video=images_from_video,
        )

        latitude_series = ldfh.get_field_from_npz_file(
            session_dir_name=self.__class__.SESSION_DIR,
            filename=LegacyDataFileSystemHelper.TAG_NPZ_FILE,
            fieldname=LegacyDataFileSystemHelper.TAG_LATITUDE_FIELD,
        )
        longitude_series = ldfh.get_field_from_npz_file(
            session_dir_name=self.__class__.SESSION_DIR,
            filename=LegacyDataFileSystemHelper.TAG_NPZ_FILE,
            fieldname=LegacyDataFileSystemHelper.TAG_LONGITUDE_FIELD,
        )
        time_series = ldfh.get_field_from_npz_file(
            session_dir_name=self.__class__.SESSION_DIR,
            filename=LegacyDataFileSystemHelper.TAG_NPZ_FILE,
            fieldname=LegacyDataFileSystemHelper.TAG_TIME_FIELD,
        )
        geo_map_scrubber = GeoMapScrubber(
            latitude_series=latitude_series,
            longitude_series=longitude_series,
            time_series=time_series,
            width=700,
        )

        self.video_plus_map_scrub_picker = VideoPlusMapScrubPicker(
            video_scrub_picker=video_scrub_picker,
            geo_map_scrubber=geo_map_scrubber,
        )

        return self

    def dont_test_visualize(self):
        self.video_plus_map_scrub_picker.run()

    def callback(self, images):
        print(images)

if __name__ == '__main__':
    unittest.main()
