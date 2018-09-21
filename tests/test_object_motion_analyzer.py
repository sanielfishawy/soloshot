import sys, math, unittest
sys.path.insert(0, '/Users/sani/dev/soloshot')

from shapely.geometry import LineString, LinearRing

from object_universe import ObjectUniverse
from camera import Camera
from image_analyzer import ImageAnalyzer
from object_motion_analyzer import ObjectMotionAnalyzer, Circumcircles
from viewable_object import RandomlyMovingObject, RandomlyMovingTag
from boundary import Boundary

from tk_canvas_renderers.element_renderers import BoundaryRenderer, CameraRenderer, ViewableObjectsRenderer, ImageRenderer, TKRenderer, CircumcircleRenderer
from tk_canvas_renderers.animator import Animator

class TestObjectMotionAnalyzer(unittest.TestCase):

    def setUp(self, num_randomly_moving_objects=10):
        self.num_randomly_moving_objects = num_randomly_moving_objects

        self.num_timestamps = 60
        self.tag_gps_angle_threshold = math.radians(7)

        self.object_universe = ObjectUniverse(num_timestamps=self.num_timestamps)

        self.camera = Camera()
        self.camera.set_actual_position((100, 400)).\
                    set_gps_position((100,380)).\
                    set_gps_max_error(25).\
                    set_fov_rad(math.pi/2)
    
        self.boundary = Boundary([(220,300), (420,100), (420,700), (220, 500)])
        
        self.tag = RandomlyMovingTag(boundary=self.boundary)
        self.viewable_objects = [self.tag]

        for _ in range(self.num_randomly_moving_objects):
            self.viewable_objects.append(RandomlyMovingObject(boundary=self.boundary))

        self.object_universe.add_camera(self.camera).\
                             add_viewable_objects(self.viewable_objects)

        for timestamp in range(self.num_timestamps):
            self.camera.set_state_of_pan_motor_angle_at_timestamp(0, timestamp)
        
        self.camera.get_computer_vision().set_cv_ids_for_all_camera_time()

        self.object_motion_analyzer = ObjectMotionAnalyzer(self.camera, 
                                                           self.tag, 
                                                           tag_gps_angle_threshold=self.tag_gps_angle_threshold)

        self.frames = self.object_motion_analyzer.get_complete_frames()

        return self

    def test_get_c1_high_def_returns_a_linear_ring(self):
        ccs = self.object_motion_analyzer.get_circumcircles_for_object_for_all_frames(self.tag)
        for cc in ccs:
            self.assertEqual(type(cc.get_c1_high_def()), LinearRing)
            
    def test_get_c1_low_def_returns_a_linear_ring(self):
        ccs = self.object_motion_analyzer.get_circumcircles_for_object_for_all_frames(self.tag)
        for cc in ccs:
            self.assertEqual(type(cc.get_c1_low_def()), LinearRing)
            
    def test_get_c2_high_def_returns_a_linear_ring(self):
        ccs = self.object_motion_analyzer.get_circumcircles_for_object_for_all_frames(self.tag)
        for cc in ccs:
            self.assertEqual(type(cc.get_c2_high_def()), LinearRing)
            
    def test_get_c2_low_def_returns_a_linear_ring(self):
        ccs = self.object_motion_analyzer.get_circumcircles_for_object_for_all_frames(self.tag)
        for cc in ccs:
            self.assertEqual(type(cc.get_c2_low_def()), LinearRing)
            
    def test_intersection_with_error_circle_for_tag_always_returns_linestring(self):
        ccs = self.object_motion_analyzer.get_circumcircles_for_object_for_all_frames(self.tag)
        for cc in ccs:
            isect = cc.get_error_circle_intersection()
            self.assertEqual(type(isect), LineString)

    def test_get_all_cirumcircles_for_object_for_all_frames_returns_list_of_cc_objects(self):
        # The setup ensures that the randomly moving tag is in every frame.
        ccs = self.object_motion_analyzer.get_circumcircles_for_object_for_all_frames(self.tag)
        self.assertGreater(len(ccs), 0)
        for cc in ccs:
            self.assertEqual(type(cc), Circumcircles)

    def test_circumcircles_added_for_each_viewable_object_in_each_frame(self):
        for frame in self.frames:
            if not self.object_motion_analyzer.is_terminal_frame(frame):
                objs = self.object_motion_analyzer.get_in_view_objects(frame)
                self.assertEqual(len(objs), self.num_randomly_moving_objects + 1)
                for obj in self.object_motion_analyzer.get_in_view_objects(frame):
                    self.assertIsInstance(self.object_motion_analyzer.get_circumcircles_for_object_in_frame(frame, obj), Circumcircles)


    def test_angle_between_positions_is_greater_than_threshold(self):
        for frame in self.frames:
            if not self.object_motion_analyzer.is_terminal_frame(frame):
                self.assertGreater(abs(self.object_motion_analyzer.get_tag_position_analyzer().get_angle_between_positions(frame)), 
                                self.tag_gps_angle_threshold)

    def test_rotation_same_as_tag_for_tag(self):
        for frame in self.frames:
            rot = self.object_motion_analyzer.get_rotation_same_as_tag(frame, self.tag)

            if self.object_motion_analyzer.is_terminal_frame(frame):
                self.assertEqual(rot, None)
            else:
                self.assertTrue(rot)
    
    def test_tag_circumcircles_always_intersect_error_circle(self):
        for frame in self.frames:
            if not self.object_motion_analyzer.is_terminal_frame(frame):
                tag = self.object_motion_analyzer.get_tag(frame)
                isects = self.object_motion_analyzer.get_circumcircles(frame)[tag].get_intersects_error_circle()
                self.assertTrue(isects)
    
    def visualize(self):
        self.boundary_renderer = BoundaryRenderer(self.boundary)
        self.camera_renderer = CameraRenderer(self.camera)
        self.viewable_objects_renderer = ViewableObjectsRenderer(self.viewable_objects, computer_vision=self.camera.get_computer_vision())
        self.image_renderer = ImageRenderer(self.camera.get_image_generator())
        self.image_renderer.set_computer_vision(self.camera.get_computer_vision())
        self.circumcircle_renderer = CircumcircleRenderer(self.object_motion_analyzer)

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