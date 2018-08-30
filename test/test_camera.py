import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
from camera import Camera
from viewable_object import StationaryObject
from object_universe import ObjectUniverse
import unittest

class TestCamera(unittest.TestCase):
    
    def setUp(self): 
        self.num_timestamps = 100
        self.object_universe = ObjectUniverse(num_timestamps=self.num_timestamps)
        self.camera = Camera(fov_deg=90, actual_position=(0,0))

        self.in_view_positions = [(1,0), (2,1), (2,-1)]
        self.out_view_positions = [(-1,0), (1,2), (1,-2)]
        self.in_view_objects  = list(map(lambda pos: StationaryObject(pos, name='in_view'), self.in_view_positions))
        self.out_view_objects = list(map(lambda pos: StationaryObject(pos, name='out_view'), self.out_view_positions))

        self.object_universe.clear_viewable_objects().add_viewable_objects(self.in_view_objects + self.out_view_objects)
        self.object_universe.add_camera(self.camera)
        
    def test_object_universe_has_correct_objects(self):
        self.assertEqual(self.object_universe.get_num_viewable_objects(), 6)
        named_out_view = list(filter(lambda obj: obj.get_name() == 'out_view', 
                                     self.object_universe.get_viewable_objects()))
        named_in_view  = list(filter(lambda obj: obj.get_name() == 'in_view', 
                                     self.object_universe.get_viewable_objects()))
        self.assertEqual(len(named_in_view), 3)
        self.assertEqual(len(named_out_view), 3)
    
    def test_camera_viewable_objects(self):
        self.assertEqual(len(self.camera.get_objects_in_view(0)), 3)
        for obj in self.camera.get_objects_in_view(0):
            self.assertEqual(obj.get_name(), 'in_view')

    def test_camera_not_viewable_objects(self):
        self.assertEqual(len(self.camera.get_objects_out_view(0)), 3)
        for obj in self.camera.get_objects_out_view(0):
            self.assertEqual(obj.get_name(), 'out_view')

    def test_camera_state_history_length_changes_when_object_universe_num_timestamps_changes(self):
        self.assertEqual(self.camera.get_state_history_len(), self.num_timestamps)
        self.object_universe.set_num_timestamps(50)
        self.assertEqual(self.camera.get_state_history_len(), 50)

if __name__ == '__main__':
    unittest.main()