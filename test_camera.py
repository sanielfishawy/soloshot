from camera import Camera
from viewable_object import StationaryObject
from object_universe import ObjectUniverse
import unittest

class TestCamera(unittest.TestCase):
    
    def setUp(self): 
        self.camera = Camera(fov_deg=90, actual_position=(0,0))

        self.in_view_positions = [(1,0), (2,1), (2,-1)]
        self.out_view_positions = [(-1,0), (1,2), (1,-2)]
        self.in_view_objects  = list(map(lambda pos: StationaryObject(pos, name='in_view'), self.in_view_positions))
        self.out_view_objects = list(map(lambda pos: StationaryObject(pos, name='out_view'), self.out_view_positions))

        ObjectUniverse().clear_objects().add_objects(self.in_view_objects + self.out_view_objects)
        
    def test_object_universe_has_correct_objects(self):
        self.assertEqual(ObjectUniverse().get_num_objects(), 6)
        named_out_view = list(filter(lambda obj: obj.get_name() == 'out_view', 
                                     ObjectUniverse().get_objects(self.camera.get_timestamp())))
        named_in_view  = list(filter(lambda obj: obj.get_name() == 'in_view', 
                                     ObjectUniverse().get_objects(self.camera.get_timestamp())))
        self.assertEqual(len(named_in_view), 3)
        self.assertEqual(len(named_out_view), 3)
    
    def test_camera_viewable_objects(self):
        self.assertEqual(len(self.camera.get_objects_in_view()), 3)
        for obj in self.camera.get_objects_in_view():
            self.assertEqual(obj.get_name(), 'in_view')


if __name__ == '__main__':
    unittest.main()