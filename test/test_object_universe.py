import sys
sys.path.insert(0, '../')
import unittest
from viewable_object import RandomlyMovingObject, StationaryObject
from boundary import Boundary
from object_universe import ObjectUniverse

class TestObjectUnivers(unittest.TestCase):

    def setUp(self):
        self.initial_num_timestamps = 100
        self.boundary = Boundary([(0,0), (100,0), (100,100), (0,100)])
        self.moving_object = RandomlyMovingObject(self.boundary, num_timestamps=self.initial_num_timestamps)
        self.stationary_object = StationaryObject((100,100), num_timestamps=self.initial_num_timestamps)
        self.viewable_objects = [self.moving_object, self.stationary_object]

    def test_object_universe_has_correct_num_timestamps(self):
        self.assertEqual(ObjectUniverse().set_num_timestamps(50).get_num_timestamps(), 50)
    
    def test_viewable_objects_have_correct_num_initial_timestamps(self):
        for vo in self.viewable_objects:
            self.assertEqual(vo.get_position_history_len(), self.initial_num_timestamps)

    def test_viewable_objects_get_history_len_from_universe_the_are_addded_to(self):
        ObjectUniverse().set_num_timestamps(50).add_viewable_objects(self.viewable_objects)
        for vo in ObjectUniverse().get_viewable_objects():
            self.assertEqual(vo.get_position_history_len(), 50)

    def test_changing_univererse_lifespan_changes_history_for_all_included_viewable_objects(self):
        ObjectUniverse().set_num_timestamps(50).add_viewable_objects(self.viewable_objects)
        ObjectUniverse().set_num_timestamps(1000)
        for vo in ObjectUniverse().get_viewable_objects():
            self.assertEqual(vo.get_position_history_len(), 1000) 

if __name__ == '__main__':
    unittest.main()