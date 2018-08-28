import unittest
from moving_object import *
from shapely.geometry import Point

class TestMovingObjectAndBoundary(unittest.TestCase):
    
    def setUp(self): 
        points = [(0,0),
                  (100,0),
                  (100,100),
                  (0,100)]
                  
        self.boundary = Boundary(points)
        self.inside_point = (50, 10)
        self.outside_point = (110, 50)

        self.moving_object = MovingObject(self.boundary)

    def test_random_point_on_boundary_is_on_boundary(self):
        rp = Point(self.boundary.random_point())
        self.assertTrue(self.boundary.exterior.contains(rp))

    # def test_angle_to_centroid(self):
    #     self.assertEqual(self.boundary.angle_to_centroid(self.outside_point), pi)

    # def test_random_distance(self):
    #     d = self.moving_object.random_distance()
    #     self.assertLessEqual(d, self.moving_object.max_distance_per_frame)
    #     self.assertGreaterEqual(d, self.moving_object.min_distance_per_frame)
    
    def test_position_history(self):
        self.moving_object.get_position_history() 

if __name__ == '__main__':
    unittest.main()