# pylint: disable=C0413
import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.getcwd())
from base import Base

class TestBase(unittest.TestCase):

    def setUp(self):
        pass

    def test_0_alignment_offset(self):
        motor_angle_series = np.array(range(10))
        base_time_series = (motor_angle_series * 100) + 123456
        alignment_offset_motor_to_video_ms = 0

        base = Base(
            gps_latitude_series=np.array([]),
            gps_longitude_series=np.array([]),
            base_gps_time_series=base_time_series,
            pan_motor_angle_series=motor_angle_series,
            alignment_offset_motor_to_video_ms=alignment_offset_motor_to_video_ms,
        )

        self.assertAlmostEqual(base.get_motor_angle_for_video_time_rad(49), np.radians(0.49))
        self.assertAlmostEqual(base.get_motor_angle_for_video_time_rad(51), np.radians(0.51))
        self.assertAlmostEqual(base.get_motor_angle_for_video_time_rad(149), np.radians(1.49))
        self.assertAlmostEqual(base.get_motor_angle_for_video_time_rad(151), np.radians(1.51))

    def test_non_0_alignment_offset(self):
        motor_angle_series = np.array(range(10))
        base_time_series = (motor_angle_series * 100) + 123456
        alignment_offset_motor_to_video_ms = 200

        base = Base(
            gps_latitude_series=np.array([]),
            gps_longitude_series=np.array([]),
            base_gps_time_series=base_time_series,
            pan_motor_angle_series=motor_angle_series,
            alignment_offset_motor_to_video_ms=alignment_offset_motor_to_video_ms,
        )

        self.assertAlmostEqual(base.get_motor_angle_for_video_time_rad(249), np.radians(0.49))
        self.assertAlmostEqual(base.get_motor_angle_for_video_time_rad(251), np.radians(0.51))
        self.assertAlmostEqual(base.get_motor_angle_for_video_time_rad(349), np.radians(1.49))
        self.assertAlmostEqual(base.get_motor_angle_for_video_time_rad(351), np.radians(1.51))

if __name__ == '__main__':
    unittest.main()
