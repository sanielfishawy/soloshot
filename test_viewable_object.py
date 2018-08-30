import unittest
from viewable_object import RandomlyMovingObject, StationaryObject
from boundary import Boundary
from shapely.geometry import Point
import math
from object_universe import ObjectUniverse

class TestStationaryObject(unittest.TestCase):
    def setUp(self):
        self.num_timestamps = 100
        self.pos = (0,0)
        self.so = StationaryObject(self.pos, num_timestamps=self.num_timestamps)
    
    def test_stationary_object_get_same_postion_for_entire_postion_history_when_created(self):
        self.assertEqual(self.so.get_num_timestamps(), self.num_timestamps)
        self.assertEqual(self.so.get_position_history_len(), self.num_timestamps)
        for timestamp in range(0, self.num_timestamps):
            self.assertEqual(self.so.get_position_at_time_stamp(timestamp), self.pos)

    def test_sationary_object_updates_postion_history_when_num_timestamps_changes(self):
        self.so.set_num_timestamps(50)
        self.assertEqual(self.so.get_position_history_len(), 50)
        for timestamp in range(0,50):
            self.assertEqual(self.so.get_position_at_time_stamp(timestamp), self.pos)

    def test_stationary_object_updates_its_num_timestamps_to_match_object_universe_it_gets_added_to(self):
        ou = ObjectUniverse(num_timestamps=200)
        ou.add_viewable_objects(self.so)
        self.assertEqual(self.so.get_position_history_len(), 200)
        for timestamp in range(0, 200):
            self.assertEqual(self.so.get_position_at_time_stamp(timestamp), self.pos)

class TestMovingObjectAndBoundary(unittest.TestCase):
    
    def setUp(self): 
        points = [(0,0),
                  (100,0),
                  (100,100),
                  (0,100)]
                  
        self.boundary = Boundary(points)
        self.inside_point = (50, 10)
        self.outside_point = (110, 50)

        self.moving_object = RandomlyMovingObject(self.boundary)

    def test_random_point_on_boundary_is_on_boundary(self):
        rp = Point(self.boundary.random_point())
        self.assertTrue(self.boundary.exterior.contains(rp))

    def test_angle_to_centroid(self):
        self.assertEqual(self.boundary.angle_to_centroid(self.outside_point), math.pi)

    def test_random_distance(self):
        d = self.moving_object.random_distance()
        self.assertLessEqual(d, self.moving_object.max_dist_per_timestamp)
        self.assertGreaterEqual(d, self.moving_object.min_dist_per_timestamp)
    
    def test_position_history(self):
        self.moving_object.get_position_history() 

if __name__ == '__main__':
    unittest.main()