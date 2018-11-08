# pylint: disable=C0413
import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.stable_fov_segmenter import StableFovSegmenter

class TestStableFovSegmenter(unittest.TestCase):

    def setUp(self):
        pass

    def test(self):
        fov_series = np.array([
            1, 1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6,
        ])
        fov_time_series = (np.array(range(fov_series.size)) + 1) * 100

        segmenter = StableFovSegmenter(
            fov_series=fov_series,
            fov_time_series=fov_time_series,
            guard_band_after_transition_ms=200,
            guard_band_before_transition_ms=300,
        )

        stable_segments = segmenter.get_stable_segments()

        expected_stable_segments = [
            {
                'fov': 1,
                'start_transition_fov_idx': 0,
                'end_transition_fov_idx': 1,
                'start_guarded_fov_time': 200,
                'end_guarded_fov_time': 0,
                'too_short': True
            },
            {
                'fov': 2,
                'start_transition_fov_idx': 1,
                'end_transition_fov_idx': 3,
                'start_guarded_fov_time': 300,
                'end_guarded_fov_time': 0,
                'too_short': True
            },
            {
                'fov': 3,
                'start_transition_fov_idx': 3,
                'end_transition_fov_idx': 6,
                'start_guarded_fov_time': 500,
                'end_guarded_fov_time': 300,
                'too_short': True
            },
            {
                'fov': 4,
                'start_transition_fov_idx': 6,
                'end_transition_fov_idx': 10,
                'start_guarded_fov_time': 800,
                'end_guarded_fov_time': 700,
                'too_short': True
            },
            {
                'fov': 5,
                'start_transition_fov_idx': 10,
                'end_transition_fov_idx': 15,
                'start_guarded_fov_time': 1200,
                'end_guarded_fov_time': 1200,
                'too_short': True
            },
            {
                'fov': 6,
                'start_transition_fov_idx': 15,
                'end_transition_fov_idx': 21,
                'start_guarded_fov_time': 1700,
                'end_guarded_fov_time': 1800,
                'too_short': False
            }
        ]

        for i, stable_segement in enumerate(stable_segments):
            for key, value in stable_segement.items():
                expected_value = expected_stable_segments[i][key]
                self.assertEqual(value, expected_value)


if __name__ == '__main__':
    unittest.main()
