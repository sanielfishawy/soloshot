# pylint: disable=C0413
import sys
import os
import unittest
import math
sys.path.insert(0, os.getcwd())

from camera import Camera
from object_universe import ObjectUniverse
from viewable_object import StationaryObject, RandomlyMovingObject, RandomlyMovingTag
from boundary import Boundary

from tk_canvas_renderers.element_renderers import ImageRenderer
from tk_canvas_renderers.render_orchestrator import RenderOrchestrator

class TestImageRenderer(unittest.TestCase):

    def setUp(self, num_randomly_moving_objects=0):

        self.num_randomly_moving_objects = num_randomly_moving_objects

        self.num_timestamps = 100
        self.object_universe = ObjectUniverse(num_timestamps=self.num_timestamps)

        self.camera = Camera()
        self.camera.set_fov_rad(math.pi / 2).\
                    set_actual_position((100,400)).\
                    set_gps_position((100,410)).\
                    set_gps_max_error(12).\
                    set_num_timestamps(self.num_timestamps)
        for timestamp in range(self.num_timestamps):
            self.camera.set_state_of_pan_motor_angle_at_timestamp(0, timestamp)

        self.viewable_objects = []
        for y in range(100, 800, 50):
            self.viewable_objects.append(StationaryObject((301, y)))

        self.boundary = Boundary([(200,200), (400,200), (400,600), (200,600)])
        for _ in range(self.num_randomly_moving_objects):
            self.viewable_objects.append(RandomlyMovingObject(boundary=self.boundary))

        self.viewable_objects.append(RandomlyMovingTag(boundary=self.boundary))

        self.object_universe.add_camera(self.camera).\
                             add_viewable_objects(self.viewable_objects)

        self.camera.get_computer_vision().set_cv_ids_for_all_camera_time()

        self.image_renderer = ImageRenderer(self.camera.get_image_generator())
        self.image_renderer.set_computer_vision(self.camera.get_computer_vision())

        return self

    def test_default_image_width_is_640(self):
        self.assertEqual(self.camera.get_image_generator().get_image_width(), 640)
        self.assertEqual(self.image_renderer.get_image_width(), 640)

    def test_all_in_view_objects_are_projected_within_image_width(self):
        x_for_all_inview_objects = self.camera.image_generator.get_x_for_all_inview_objects_for_all_camera_time()

        for x_s in x_for_all_inview_objects:
            for obj in x_s.keys():
                self.assertLess(abs(x_s[obj]), self.image_renderer.get_image_width() / 2)


    def visualize(self):
        renderable_objects = [
            self.boundary,
            self.object_universe,
        ]

        RenderOrchestrator(
            self.num_timestamps,
            seconds_per_timestamp=0.2,
            renderable_objects=renderable_objects).run()


if __name__ == '__main__':
    unittest.main()
