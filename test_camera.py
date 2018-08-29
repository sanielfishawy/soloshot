from camera import Camera
from viewable_object import StationaryObject
import unittest

class TestCamera(unittest.TestCase):
    
    def setUp(self): 
        self.camera = Camera(fov_deg=90, actual_position=(0,0))

        self.in_view_positions = [(1,0), (2,1), (2,-1)]
        self.out_view_positions = [(-1,0), (1,2), (1,-2)]
        self.in_view_object = StationaryObject((1,0), name='in_view')  
        self.in_view_object1 = StationaryObject((1,0), name='in_view') 
    
    def test_camera_viewable_objects(self):
        pass


if __name__ == '__main__':
    unittest.main()