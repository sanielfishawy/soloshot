# pylint: disable=C0413, C0103
import sys
import os
import unittest
sys.path.insert(0, os.getcwd())

from object_universe import ObjectUniverse
from camera import Camera
from viewable_object import ViewableObject
from computer_vision import ComputerVision

class TestComputerVision(unittest.TestCase):

    def setUp(self):
        self.num_timestamps = 6
        self.object_universe = ObjectUniverse(num_timestamps=self.num_timestamps)
        self.camera = Camera(fov_deg=90, actual_position=(0,0))
        self.cv = ComputerVision()
        self.camera.set_computer_vision(self.cv)
        self.object_universe.add_camera(self.camera)

        for timestamp, _ in enumerate(self.camera.get_state_history()):
            self.camera.set_pan_angle_deg(0, timestamp)

        self.out_pos = (1,2)
        self.in_pos = (1,0)

        self.out_obj = ViewableObject()
        self.in_obj = ViewableObject()
        self.in_out_in_obj = ViewableObject()
        self.out_in_out_obj = ViewableObject()

        self.viewable_objects = [
            self.out_obj,
            self.in_obj,
            self.in_out_in_obj,
            self.out_in_out_obj,
        ]

        self.object_universe.add_viewable_objects(self.viewable_objects)

        for timestamp, _ in enumerate(self.out_obj.position_history):
            self.in_obj.set_position_at_timestamp(self.in_pos, timestamp)
            self.out_obj.set_position_at_timestamp(self.out_pos, timestamp)

        for timestamp in [0,1]:
            self.in_out_in_obj.set_position_at_timestamp(self.in_pos, timestamp)
            self.out_in_out_obj.set_position_at_timestamp(self.out_pos, timestamp)

        for timestamp in [2,3]:
            self.in_out_in_obj.set_position_at_timestamp(self.out_pos, timestamp)
            self.out_in_out_obj.set_position_at_timestamp(self.in_pos, timestamp)

        for timestamp in [4,5]:
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
        for timestamp in [0,1]:
            self.assertIsNone(self.cv.get_cv_id_for_obj_at_timestamp(self.out_in_out_obj, timestamp))
            self.assertIsNotNone(self.cv.get_cv_id_for_obj_at_timestamp(self.in_out_in_obj, timestamp))

        self.assertEqual(self.cv.get_cv_id_for_obj_at_timestamp(self.in_out_in_obj, 0),
                         self.cv.get_cv_id_for_obj_at_timestamp(self.in_out_in_obj, 1))

    def that_it_prefixes_the_ids_with_cv(self):
        self.assertEqual(self.cv.get_cv_id_for_obj_at_timestamp(self.in_obj,0)[0:2], 'cv')

    def test_it_retains_ids_of_objects_that_remain_in_view(self):
        self.assertEqual(self.cv.get_cv_id_for_obj_at_timestamp(self.out_in_out_obj, 2),
                         self.cv.get_cv_id_for_obj_at_timestamp(self.out_in_out_obj, 3))


    def test_it_removes_ids_of_objects_that_leave_view(self):
        self.assertIsNone(self.cv.get_cv_id_for_obj_at_timestamp(self.out_in_out_obj, 4))
        self.assertIsNone(self.cv.get_cv_id_for_obj_at_timestamp(self.out_in_out_obj, 5))

    def test_it_re_ids_objects_that_come_back_in_view(self):
        in_first = self.cv.get_cv_id_for_obj_at_timestamp(self.in_out_in_obj, 1)
        in_again = self.cv.get_cv_id_for_obj_at_timestamp(self.in_out_in_obj, 4)
        self.assertIsNotNone(in_first)
        self.assertIsNotNone(in_again)
        self.assertNotEqual(in_first, in_again)


if __name__ == '__main__':
    unittest.main()
