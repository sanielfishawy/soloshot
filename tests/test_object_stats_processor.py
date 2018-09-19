import sys, math, unittest
sys.path.insert(0, '/Users/sani/dev/soloshot')

from object_universe import ObjectUniverse
from camera import Camera
from image_analyzer import ImageAnalyzer
from object_motion_analyzer import ObjectMotionAnalyzer
from viewable_object import RandomlyMovingObject, RandomlyMovingTag
from boundary import Boundary
from object_stats_processor import ObjectsStatsProcessor

from tk_canvas_renderers.element_renderers import BoundaryRenderer, CameraRenderer, ViewableObjectsRenderer, ImageRenderer, TKRenderer, CircumcirleRenderer
from tk_canvas_renderers.animator import Animator

class TestBaseCalibrator(unittest.TestCase):

    def setUp(self):
        self.num_timestamps = 50
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
        for _ in range(20):
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

        self.object_stats_processor = ObjectsStatsProcessor(self.object_motion_analyzer)

        return self
    
    def test_get_all_eliminated_before_timestamp(self):
        for timestamp in range(self.num_timestamps):
            eliminated = []
            for obj in self.object_stats_processor.get_processed_objects():
                if self.object_stats_processor.get_elimination_t(obj) != None and self.object_stats_processor.get_elimination_t(obj) <= timestamp:
                    eliminated.append(obj)
            
            eliminated.sort(key=self.get_id)
            es = self.object_stats_processor.get_all_eliminated_before_timestamp(timestamp)
            es.sort(key=self.get_id) 
            self.assertEqual(eliminated, es)

    def get_id(self, obj):
        return id(obj)

    def test_tag_is_top_ranked_object(self):
        self.assertEqual(self.object_stats_processor.get_top_ranked_object(), self.tag)
    
    def test_all_ranked_objects_always_moved_same_direction_as_tag(self):
        ranked = self.object_stats_processor.get_ranked_objects()
        for obj in ranked:
            self.assertTrue(self.object_stats_processor.get_didnt_move_opposite_to_tag(obj))
    
    def test_all_objects_eliminated_for_opposite_are_marked_eliminated_with_same_time_as_opposite_time(self):
        for obj in self.object_stats_processor.get_all_moved_oposite():
            self.assertTrue(self.object_stats_processor.get_did_move_opposite_to_tag(obj))
            self.assertEqual(self.object_stats_processor.get_moved_opposite_to_tag_t(obj),
                             self.object_stats_processor.get_elimination_t(obj))
    
    def test_didnt_intersect_t_is_an_int_or_none(self):
        for obj in self.object_stats_processor.get_processed_objects():
            if self.object_stats_processor.get_didnt_intersect_error_circle_t(obj) != None:
                self.assertEqual(type(self.object_stats_processor.get_didnt_intersect_error_circle_t(obj)), int)

    def test_all_objects_never_moved_in_opposite_direction_are_marked_eliminated_if_they_have_fewer_intersections_than_top_ranked_objects(self):
        for obj in self.object_stats_processor.get_all_that_always_moved_same_direction_as_tag():
            if obj not in self.object_stats_processor.get_top_ranked_objects():
                self.assertTrue(self.object_stats_processor.get_eliminated(obj))
                last_frame = self.object_stats_processor.get_object_motion_analyzer().get_tag_position_analyzer().get_last_complete_frame()
                early_time_of_last_frame = self.object_stats_processor.get_object_motion_analyzer().get_tag_position_analyzer().get_early_min_max_timestamp(last_frame)
                self.assertEqual(early_time_of_last_frame, self.object_stats_processor.get_elimination_t(obj))
        
    def test_tag_always_intersects(self):
        o = self.object_stats_processor.get_processed_objects()
        t = self.object_stats_processor.get_didnt_intersect_error_circle_n(self.tag)
        self.assertEqual(self.object_stats_processor.get_didnt_intersect_error_circle_n(self.tag), 0)
        
    def test_get_to_ranked_objects_returns_all_with_same_didnt_intersect_n_as_top_ranked_object(self):
        top_ranked = self.object_stats_processor.get_top_ranked_object()
        top_ranked_n = self.object_stats_processor.get_didnt_intersect_error_circle_n(top_ranked)
        
        ranked_objs = self.object_stats_processor.get_ranked_objects()
        num_ranked_objs = len(ranked_objs)

        moved_opposite = self.object_stats_processor.get_all_moved_oposite()[0]

        for obj in ranked_objs:
            self.object_stats_processor._processed_objects[obj][self.object_stats_processor.didnt_intersect_error_circle_n] = top_ranked_n

        self.assertEqual(num_ranked_objs, len(self.object_stats_processor.get_top_ranked_objects()))

        self.object_stats_processor._processed_objects[moved_opposite][self.object_stats_processor.didnt_intersect_error_circle_n] = top_ranked_n
        self.object_stats_processor._processed_objects[moved_opposite][self.object_stats_processor.eliminated] = False
        self.object_stats_processor._processed_objects[moved_opposite][self.object_stats_processor.moved_opposite_to_tag_n] = 0
        self.object_stats_processor._processed_objects[moved_opposite][self.object_stats_processor.moved_opposite_to_tag_t] = None

        self.assertEqual(num_ranked_objs + 1, len(self.object_stats_processor.get_top_ranked_objects()))

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