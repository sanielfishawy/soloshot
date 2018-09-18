import sys, math, unittest
sys.path.insert(0, '/Users/sani/dev/soloshot')

from object_universe import ObjectUniverse
from camera import Camera
from image_analyzer import ImageAnalyzer
from object_motion_analyzer import ObjectMotionAnalyzer
from viewable_object import RandomlyMovingObject, RandomlyMovingTag
from boundary import Boundary
from base_calibrator import ObjectsStatsProcessor

from tk_canvas_renderers.element_renderers import BoundaryRenderer, CameraRenderer, ViewableObjectsRenderer, ImageRenderer, TKRenderer, CircumcirleRenderer
from tk_canvas_renderers.animator import Animator

class TestBaseCalibrator(unittest.TestCase):

    def setUp(self):
        self.num_timestamps = 40
        self.tag_gps_angle_threshold = math.radians(10)

        self.object_universe = ObjectUniverse(num_timestamps=self.num_timestamps)

        self.camera = Camera()
        self.camera.set_actual_position((100, 400)).\
                    set_gps_position((100,380)).\
                    set_gps_max_error(25).\
                    set_fov_rad(math.pi/2)
    
        self.boundary = Boundary([(220,300), (420,100), (420,700), (220, 500)])
        
        self.tag = RandomlyMovingTag(boundary=self.boundary)
        self.r_objs = []
        for _ in range(10):
            self.r_objs.append(RandomlyMovingObject(boundary=self.boundary))
        
        self.viewable_objects = [self.tag] + self.r_objs

        self.object_universe.add_camera(self.camera).\
                             add_viewable_objects(self.viewable_objects)

        for timestamp in range(self.num_timestamps):
            self.camera.set_state_of_pan_motor_angle_at_timestamp(0, timestamp)
        
        self.camera.get_computer_vision().set_cv_ids_for_all_camera_time()

        self.image_analyzer = ImageAnalyzer(self.camera)
        
        self.object_motion_analyzer = ObjectMotionAnalyzer(self.camera, 
                                                           self.tag, 
                                                           tag_gps_angle_threshold=self.tag_gps_angle_threshold)

        self.frames = self.object_motion_analyzer.get_frames()

        self.object_stats_processor = ObjectsStatsProcessor(self.object_motion_analyzer)

        return self

    def dont_test_tag_is_top_ranked_object(self):
        self.assertEqual(self.object_stats_processor.get_top_ranked_object(), self.tag)
    
    def dont_test_all_ranked_objects_always_moved_same_direction_as_tag(self):
        ranked = self.object_stats_processor.get_ranked_objects()
        print(len(ranked))
        for obj in ranked:
            self.assertTrue(self.object_stats_processor.get_didnt_move_opposite_to_tag(obj))
    
    def test_foo(self):
        pass

    def visualize(self):
        self.boundary_renderer = BoundaryRenderer(self.boundary)
        self.camera_renderer = CameraRenderer(self.camera)
        self.viewable_objects_renderer = ViewableObjectsRenderer(self.viewable_objects, computer_vision=self.camera.get_computer_vision())
        self.image_renderer = ImageRenderer(self.camera.get_image_generator())
        self.image_renderer.set_computer_vision(self.camera.get_computer_vision())
        self.circumcircle_renderer = CircumcirleRenderer(self.object_motion_analyzer)

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