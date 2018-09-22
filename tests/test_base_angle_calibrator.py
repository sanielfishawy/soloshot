import sys, math, unittest
sys.path.insert(0, '/Users/sani/dev/soloshot')

from base_position_calibrator import BasePositionCalibrator
from base_angle_calibrator import BaseAngleCalibrator
from object_universe import ObjectUniverse
from camera import Camera
from viewable_object import RandomlyMovingTag
from boundary import Boundary

from tk_canvas_renderers.element_renderers import BoundaryRenderer, CameraRenderer, ViewableObjectsRenderer, ImageRenderer, TKRenderer, BasePositionCalibratorRenderer 
from tk_canvas_renderers.animator import Animator

from object_motion_analyzer import Circumcircles

class TestBaseAngleCalibrator(unittest.TestCase):

    def setUp(self):

        self.num_timestamps = 50
        self.tag_gps_angle_threshold = math.radians(6)

        self.object_universe = ObjectUniverse(num_timestamps=self.num_timestamps)

        self.compass_error = 3.7
        self.camera = Camera()
        self.camera.set_actual_position((100, 400)).\
                    set_gps_position((100,380)).\
                    set_gps_max_error(25).\
                    set_fov_rad(math.pi/2).\
                    set_compass_error_rad(math.radians(self.compass_error))
    
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
        self.boundary_renderer = BoundaryRenderer(self.boundary)
        self.camera_renderer = CameraRenderer(self.camera)
        self.viewable_objects_renderer = ViewableObjectsRenderer(self.viewable_objects, computer_vision=self.camera.get_computer_vision())
        self.image_renderer = ImageRenderer(self.camera.get_image_generator())
        self.image_renderer.set_computer_vision(self.camera.get_computer_vision())
        self.circumcircle_renderer = BasePositionCalibratorRenderer(self.base_position_calibrator.get_object_motion_analyzer())

        self.renderers = [
                            self.camera_renderer,
                            self.viewable_objects_renderer,
                            self.boundary_renderer,
                            self.image_renderer,
                            self.circumcircle_renderer,
        ]

        self.animator = Animator(element_renderers=self.renderers, num_timestamps=self.num_timestamps, seconds_per_timestamp=0.2)

        TKRenderer().set_canvas_height(900).\
                     set_canvas_width(1000).\
                     set_scale(1).\
                     set_mouse_click_callback(self.animator.play).\
                     start_tk_event_loop()

if __name__ == '__main__':
    unittest.main()