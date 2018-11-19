# pylint: disable=C0413
import sys
import math
import unittest
sys.path.insert(0, '/Users/sani/dev/soloshot')

from base_position_calibrator import BasePositionCalibrator
from base_angle_calibrator import BaseAngleCalibrator
from object_universe import ObjectUniverse
from camera import Camera
from viewable_object import RandomlyMovingTag
from boundary import Boundary

from tk_canvas_renderers.render_orchestrator import RenderOrchestrator


class TestBaseAngleCalibrator(unittest.TestCase):

    def setUp(self, tag_gps_angle_threshold=6, compass_err_deg=3.7):
        self.tag_gps_angle_threshold = tag_gps_angle_threshold
        self.compass_err_deg = compass_err_deg

        self.num_timestamps = 50
        self.tag_gps_angle_threshold = math.radians(self.tag_gps_angle_threshold)

        self.object_universe = ObjectUniverse(num_timestamps=self.num_timestamps)

        self.camera = Camera()
        self.camera.set_actual_position((100, 400)).\
                    set_gps_position((100,380)).\
                    set_gps_max_error(25).\
                    set_fov_rad(math.pi/2).\
                    set_compass_error_rad(math.radians(self.compass_err_deg))

        self.boundary = Boundary([(220,300), (420,100), (420,700), (220, 500)])

        self.tag = RandomlyMovingTag(boundary=self.boundary)
        self.viewable_objects = [self.tag]

        self.object_universe.add_camera(self.camera).\
                             add_viewable_objects(self.viewable_objects)

        for timestamp in range(self.num_timestamps):
            self.camera.set_state_of_pan_motor_angle_at_timestamp(0, timestamp)

        self.camera.get_computer_vision().set_cv_ids_for_all_camera_time()

        self.base_position_calibrator = BasePositionCalibrator(self.camera,
                                                               self.tag,
                                                               tag_gps_angle_threshold=self.tag_gps_angle_threshold)


        self.base_angle_calibrator = BaseAngleCalibrator(self.base_position_calibrator)

        return self

    def test_base_angle_calibrator_result_is_almost_equal_to_compass_error(self):
        calibrated_error = self.base_angle_calibrator.get_base_angle_error()
        compass_error = self.camera.get_compass_error_rad()
        self.assertAlmostEqual(calibrated_error, compass_error)

    def test_get_frame_returns_a_complete_frame(self):
        frame = self.base_angle_calibrator._get_frame()
        self.assertEqual(type(frame), dict)
        self.assertGreater(len(frame), 0)

    def test_get_tag_angle_relative_to_center_in_image_returns_an_angle(self):
        angle = self.base_angle_calibrator._get_tag_angle_relative_to_center_in_image()
        self.assertEqual(type(angle), float)

    def visualize(self):

        renderable_objects = [
            self.boundary,
            self.object_universe,
            self.base_position_calibrator,
        ]

        RenderOrchestrator(self.num_timestamps,
                           seconds_per_timestamp=0.2,
                           renderable_objects=renderable_objects).run()

if __name__ == '__main__':
    unittest.main()