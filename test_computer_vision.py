import unittest
from object_universe import ObjectUniverse
from camera import Camera
from viewable_object import ViewableObject
from computer_vision import ComputerVision

class TestComputerVision(unittest.TestCase):

    def setUp(self):
        self.num_timestamps = 6
        self.object_universe = ObjectUniverse(num_timestamps=self.num_timestamps)
        self.camera = Camera(fov_deg=90, actual_position=(0,0))
        self.cv = ComputerVision(camera=self.camera)
        self.object_universe.add_camera(self.camera)

        for timestamp, _ in enumerate(self.camera.get_state_history()):
            self.camera.set_pan_angle_deg(0, timestamp)
        
        self.out_pos = (1,2)
        self.in_pos = (1,0)

        self.out_obj = ViewableObject()
        self.in_obj = ViewableObject()
        self.in_out_in_obj = ViewableObject()
        self.out_in_out_obj = ViewableObject()

        self.viewable_objects = [ self.out_obj, self.in_obj, self.in_out_in_obj, self.out_in_out_obj ]

        self.object_universe.add_viewable_objects(self.viewable_objects)

        for timestamp, _ in enumerate(self.out_obj.position_history):
            self.in_obj.set_position_at_timestamp(self.in_pos, timestamp)
            self.out_obj.set_position_at_timestamp(self.out_pos, timestamp)

        for timestamp in range(0,2):
            self.in_out_in_obj.set_position_at_timestamp(self.in_pos, timestamp)
            self.out_in_out_obj.set_position_at_timestamp(self.out_pos, timestamp)

        for timestamp in range(2,4):
            self.in_out_in_obj.set_position_at_timestamp(self.out_pos, timestamp)
            self.out_in_out_obj.set_position_at_timestamp(self.in_pos, timestamp)

        for timestamp in range(4,6):
            self.in_out_in_obj.set_position_at_timestamp(self.in_pos, timestamp)
            self.out_in_out_obj.set_position_at_timestamp(self.out_pos, timestamp)

        self.cv.set_cv_ids_for_all_camera_time()

    def test_camera_has_correct_number_of_timestamps(self):
        self.assertEqual(self.camera.get_num_timestamps(), self.num_timestamps)
        self.assertEqual(self.camera.get_state_history_len(), self.num_timestamps)

    def test_viewable_objects_have_correct_number_of_timestamps(self):
        for vo in self.viewable_objects:
            self.assertEqual(vo.get_position_history_len(), self.num_timestamps)
            self.assertEqual(vo.get_num_timestamps(), self.num_timestamps)
        
    def test_objects_that_never_are_in_view_never_get_id(self):
        for timestamp, _ in enumerate(self.out_obj.get_position_history()):
            self.assertIsNone(self.cv.get_cv_id_for_obj_at_timestamp(self.out_obj, timestamp))
            
    def test_it_ids_objects_that_come_into_view(self):
        pass

    def test_it_retains_ids_of_objects_that_remain_in_view(self):
        pass
    
    def test_it_removes_ids_of_objects_that_leave_view(self):
        pass
    
    def test_it_re_ids_objects_that_come_back_in_view(self):
        pass


if __name__ == '__main__':
    unittest.main()
