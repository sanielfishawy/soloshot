# pylint: disable=C0413, C0301, W0212
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

    def test_get_frames_with_min_distance_to_camera(self):
        spiral_positions = []
        for n, angle in enumerate(self.angles):
            spiral_radius = n + 1
            spiral_positions.append(
                GU.point_with_angle_and_distance_from_point(
                    point=self.camera_pos,
                    angle_rad=angle,
                    d=spiral_radius,
                )
            )
        for timestamp, pos in enumerate(spiral_positions):
            self.vo.set_position_at_timestamp(pos, timestamp)

        tag_position_analyzer = TagPositionAnalyzer(self.vo, self.camera)

        frames = tag_position_analyzer.get_frames_where_range_exceeds_threshold(
            threshold_rad=(2 * math.pi / self.number_of_slices_of_circle) - .01,
            min_distance_to_camera=20,
        )
        self.assertEqual(
            tag_position_analyzer.get_early_min_max_timestamp(frames[0]),
            19,
        )

    def test_timestamps_with_greater_distance(self):
        timestamps = self.tag_position_analyzer._get_timestamps_between_timestamps_with_distance_greater_than_min(
            timestamp1=0,
            timestamp2=self.num_timestamps-1,
            min_distance_to_camera=self.radius-1,
        )
        self.assertEqual(timestamps.size, self.num_timestamps)

        timestamps = self.tag_position_analyzer._get_timestamps_between_timestamps_with_distance_greater_than_min(
            timestamp1=0,
            timestamp2=self.num_timestamps-1,
            min_distance_to_camera=self.radius+1,
        )
        self.assertEqual(timestamps.size, 0)

    def test_tag_distances_to_camera(self):
        distances = self.tag_position_analyzer._get_tag_distances_to_camera()
        self.assertEqual(distances.size, self.num_timestamps)
        for distance in distances:
            self.assertAlmostEqual(distance, self.radius)

    def test_get_tag_angles(self):
        angles = self.tag_position_analyzer._get_tag_angles()
        self.assertEqual(angles.size, self.num_timestamps)
        for n, angle in enumerate(angles):
            self.assertAlmostEqual(angle, self.get_raw_angle_of_point(n))

    def test_get_quadrants(self):
        quads = self.tag_position_analyzer._get_tag_quadrants()
        self.assertEqual(quads.size, self.num_timestamps)

    def test_get_list_of_angles(self):
        angles = self.tag_position_analyzer._list_of_angles_between_timestamps(
            timestamp1=0,
            timestamp2=self.num_timestamps,
            min_distance_to_camera=0,
        )
        self.assertEqual(angles.size, self.num_timestamps)

    def test_range_of_angles_between_timestamps(self):
        for i in range(40):
            self.assertAlmostEqual(
                self.tag_position_analyzer._range_of_angles_between_timestamps(
                    timestamp1=i,
                    timestamp2=i+1,
                    min_distance_to_camera=0
                ),
                2 * math.pi/self.number_of_slices_of_circle
            )
            self.assertAlmostEqual(
                self.tag_position_analyzer._range_of_angles_between_timestamps(
                    timestamp1=i,
                    timestamp2=i+2,
                    min_distance_to_camera=0,
                ),
                2 * 2 * math.pi/self.number_of_slices_of_circle
            )
            self.assertAlmostEqual(
                self.tag_position_analyzer._range_of_angles_between_timestamps(
                    timestamp1=i,
                    timestamp2=i+3,
                    min_distance_to_camera=0
                ),
                2 * 3 * math.pi/self.number_of_slices_of_circle,
            )

    def test_first_time_after_timestamp_where_range_exceeds_threshold(self):
        t = self.tag_position_analyzer._first_time_after_timestamp_where_range_of_angles_exceeds_threshold(
            timestamp=0,
            threshold=math.pi/self.number_of_slices_of_circle - 0.01,
            min_distance_to_camera=0,
        )
        self.assertEqual(t, 1)

    def test_range_of_angles_in_frame_just_exeeds_threshold(self):
        for n in range(2, 6):
            frames = self.tag_position_analyzer.get_frames_where_range_exceeds_threshold(
                threshold_rad=(n * 2 * math.pi / self.number_of_slices_of_circle) - .01,
                min_distance_to_camera=0,
            )
            for frame in frames:
                if self.tag_position_analyzer.get_frame_end_timestamp(frame) != None:
                    self.assertEqual(n, self.tag_position_analyzer.get_frame_end_timestamp(frame) -
                                        self.tag_position_analyzer.get_frame_start_timestamp(frame))

    def test_min_and_max_positions_in_frame(self):
        for n in range(2,6):
            frames = self.tag_position_analyzer.get_frames_where_range_exceeds_threshold(
                threshold_rad=(n * math.pi / self.number_of_slices_of_circle) -.01,
                min_distance_to_camera=0,
            )
            for frame in frames:
                if self.tag_position_analyzer.get_frame_end_timestamp(frame) is not None:
                    self.assertEqual(self.tag_position_analyzer.get_timestamp_of_min_angle(frame),
                                     self.tag_position_analyzer.get_frame_start_timestamp(frame))
                    self.assertEqual(self.tag_position_analyzer.get_timestamp_of_max_angle(frame),
                                     self.tag_position_analyzer.get_frame_end_timestamp(frame))
                    self.assertGreater(self.tag_position_analyzer.get_late_min_max_timestamp(frame),
                                       self.tag_position_analyzer.get_early_min_max_timestamp(frame))
    def test_distance_in_frame(self):
        for n in range(2,6):
            frames = self.tag_position_analyzer.get_frames_where_range_exceeds_threshold(
                threshold_rad=(2 * n * math.pi / self.number_of_slices_of_circle) -.01,
                min_distance_to_camera=0,
            )
            for frame in frames:
                if self.tag_position_analyzer.get_frame_end_timestamp(frame) != None:
                    self.assertAlmostEqual(self.tag_position_analyzer.get_distance_between_positions(frame),
                                           self.get_distance_between_points(n))

    def test_angle_betwen_points_counter_clockwise_rotation(self):
        for n in range(2,6):
            frames = self.tag_position_analyzer.get_frames_where_range_exceeds_threshold(
                threshold_rad=(2 * n * math.pi / self.number_of_slices_of_circle) -.01,
                min_distance_to_camera=0,
            )
            for frame in frames:
                if self.tag_position_analyzer.get_frame_end_timestamp(frame) != None:
                    self.assertAlmostEqual(self.tag_position_analyzer.get_angle_between_positions(frame),
                                           self.get_angle_between_points(n))

    def test_angle_betwen_points_clockwise_rotation(self):
        for timestamp, pos in enumerate(reversed(self.positions)):
            self.vo.set_position_at_timestamp(pos, timestamp)

        tag_position_analyzer = TagPositionAnalyzer(self.vo, self.camera)

        for n in range(2, 6):
            threshold = (2 * n * math.pi / self.number_of_slices_of_circle) -.01
            frames = tag_position_analyzer.get_frames_where_range_exceeds_threshold(
                threshold_rad=threshold,
                min_distance_to_camera=0,
            )
            for frame in frames:
                if tag_position_analyzer.get_frame_end_timestamp(frame) is not None:
                    self.assertAlmostEqual(tag_position_analyzer.get_angle_between_positions(frame),
                                           -self.get_angle_between_points(n))

    def get_raw_angle_of_point(self, n):
        r = n * 2 * math.pi / self.number_of_slices_of_circle
        if r > 2 * math.pi:
            r = r - ( 2* math.pi )
        return r

    def get_angle_between_points(self, n):
        return n * 2 * math.pi / self.number_of_slices_of_circle

    def get_distance_between_points(self, n):
        return 2 * self.radius * math.sin(self.get_angle_between_points(n) /2)

if __name__ == '__main__':
    unittest.main()