# pylint: disable=C0413, W0212
import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.getcwd())
from tag import Tag

class TestTag(unittest.TestCase):

    def setUp(self):
        self.tag_time_series = (np.array(list(range(20))) + 1) * 100
        self.alignment_offset_video_to_tag_ms = -60
        self.tag = Tag(
            latitude_series=None,
            longitude_series=None,
            time_series=self.tag_time_series,
            alignment_offset_video_to_tag_ms=self.alignment_offset_video_to_tag_ms
        )

    def test_get_normalized_time_series(self):
        expected_normalized_time_series = self.tag_time_series - self.tag_time_series[0]
        np.testing.assert_array_equal(
            self.tag._get_normalized_time_series(),
            expected_normalized_time_series
        )

    def test_get_tag_time_for_video_time(self):
        video_time = 200
        expected_tag_time = video_time + self.alignment_offset_video_to_tag_ms
        np.testing.assert_array_equal(
            self.tag.get_tag_time_for_video_time(video_time),
            expected_tag_time,
        )

    def test_get_idx_before_video_time(self):
        video_time = 200
        self.assertEqual(self.tag.get_idx_before_video_time(video_time), 1)

    def test_get_idx_after_video_time(self):
        video_time = 200
        self.assertEqual(self.tag.get_idx_after_video_time(video_time), 2)

if __name__ == '__main__':
    unittest.main()
