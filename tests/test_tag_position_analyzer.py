# pylint: disable=C0413
import sys
import os
import unittest
import math
sys.path.insert(0, os.getcwd())

import geometry_utils as GU
from tag_position_analyzer import TagPositionAnalyzer
from camera import Camera
from viewable_object import ViewableObject


class TestTagPositionAnalyzer(unittest.TestCase):

    def setUp(self):
        self.num_timestamps = 64
        self.number_of_slices_of_circle = 32
        self.radius = 100

        self.camera_pos = (100,100)
        self.camera = Camera()
        self.camera.set_gps_position(self.camera_pos)

        self.vo = ViewableObject(num_timestamps=self.num_timestamps)

        self.angles = [n * 2 * math.pi / self.number_of_slices_of_circle for n in range (self.num_timestamps)]
        self.positions = [GU.point_with_angle_and_distance_from_point(self.camera_pos, angle, self.radius) for angle in self.angles]

        self.tag_position_analyzer = TagPositionAnalyzer(self.vo, self.camera)

        for timestamp, pos in enumerate(self.positions):
            self.vo.set_position_at_timestamp(pos, timestamp)

    def test_range_of_angles_between_timestamps(self):
        for i in range(40):
            self.assertAlmostEqual(self.tag_position_analyzer._range_of_angles_between_timestamps(i,i+1), 2 * math.pi/self.number_of_slices_of_circle)
            self.assertAlmostEqual(self.tag_position_analyzer._range_of_angles_between_timestamps(i,i+2), 2 * 2 * math.pi/self.number_of_slices_of_circle)
            self.assertAlmostEqual(self.tag_position_analyzer._range_of_angles_between_timestamps(i,i+3), 2 * 3 * math.pi/self.number_of_slices_of_circle)

    def test_first_time_after_timestamp_where_range_exceeds_threshold(self):
        t = self.tag_position_analyzer._first_time_after_timestamp_where_range_of_angles_exceeds_threshold(0, math.pi/self.number_of_slices_of_circle - 0.01)
        self.assertEqual(t, 1)

    def test_range_of_angles_in_frame_just_exeeds_threshold(self):
        for n in range(2, 6):
            frames = self.tag_position_analyzer.get_frames_where_range_exceeds_threshold((n * 2 * math.pi / self.number_of_slices_of_circle) - .01)
            for frame in frames:
                if self.tag_position_analyzer.get_frame_end_timestamp(frame) != None:
                    self.assertEqual(n, self.tag_position_analyzer.get_frame_end_timestamp(frame) -
                                        self.tag_position_analyzer.get_frame_start_timestamp(frame))

    def test_min_and_max_positions_in_frame(self):
        for n in range(2,6):
            frames = self.tag_position_analyzer.get_frames_where_range_exceeds_threshold((n * math.pi / self.number_of_slices_of_circle) -.01)
            for frame in frames:
                if self.tag_position_analyzer.get_frame_end_timestamp(frame) != None:
                    self.assertEqual(self.tag_position_analyzer.get_timestamp_of_min_angle(frame),
                                     self.tag_position_analyzer.get_frame_start_timestamp(frame))
                    self.assertEqual(self.tag_position_analyzer.get_timestamp_of_max_angle(frame),
                                     self.tag_position_analyzer.get_frame_end_timestamp(frame))
                    self.assertGreater(self.tag_position_analyzer.get_late_min_max_timestamp(frame),
                                       self.tag_position_analyzer.get_early_min_max_timestamp(frame))
    def test_distance_in_frame(self):
        for n in range(2,6):
            frames = self.tag_position_analyzer.get_frames_where_range_exceeds_threshold((2 * n * math.pi / self.number_of_slices_of_circle) -.01)
            for frame in frames:
                if self.tag_position_analyzer.get_frame_end_timestamp(frame) != None:
                    self.assertAlmostEqual(self.tag_position_analyzer.get_distance_between_positions(frame),
                                           self.get_distance_between_points(n))

    def test_angle_betwen_points_counter_clockwise_rotation(self):
        for n in range(2,6):
            frames = self.tag_position_analyzer.get_frames_where_range_exceeds_threshold((2 * n * math.pi / self.number_of_slices_of_circle) -.01)
            for frame in frames:
                if self.tag_position_analyzer.get_frame_end_timestamp(frame) != None:
                    self.assertAlmostEqual(self.tag_position_analyzer.get_angle_between_positions(frame),
                                           self.get_angle_between_points(n))

    def test_angle_betwen_points_clockwise_rotation(self):
        for timestamp, pos in enumerate(reversed(self.positions)):
            self.vo.set_position_at_timestamp(pos, timestamp)

        for n in range(2,6):
            frames = self.tag_position_analyzer.get_frames_where_range_exceeds_threshold((2 * n * math.pi / self.number_of_slices_of_circle) -.01)
            for frame in frames:
                if self.tag_position_analyzer.get_frame_end_timestamp(frame) != None:
                    self.assertAlmostEqual(self.tag_position_analyzer.get_angle_between_positions(frame),
                                           -self.get_angle_between_points(n))

    def get_angle_between_points(self, n):
        return n * 2 * math.pi / self.number_of_slices_of_circle

    def get_distance_between_points(self, n):
        return 2 * self.radius * math.sin(self.get_angle_between_points(n) /2)

if __name__ == '__main__':
    unittest.main()