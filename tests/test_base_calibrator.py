import sys, math, unittest
sys.path.insert(0, '/Users/sani/dev/soloshot')

from base_calibrator import BaseCalibrator
from object_universe import ObjectUniverse
from camera import Camera
from viewable_object import RandomlyMovingObject, RandomlyMovingTag
from boundary import Boundary

from tk_canvas_renderers.element_renderers import BoundaryRenderer, CameraRenderer, ViewableObjectsRenderer, ImageRenderer, TKRenderer, CircumcircleRenderer 
from tk_canvas_renderers.animator import Animator

from object_motion_analyzer import Circumcircles
from shapely.geometry import LineString, Point, MultiPoint
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
        for _ in range(1):
            self.r_objs.append(RandomlyMovingObject(boundary=self.boundary))
        
        self.viewable_objects = [self.tag] + self.r_objs

        self.object_universe.add_camera(self.camera).\
                             add_viewable_objects(self.viewable_objects)

        for timestamp in range(self.num_timestamps):
            self.camera.set_state_of_pan_motor_angle_at_timestamp(0, timestamp)
        
        self.camera.get_computer_vision().set_cv_ids_for_all_camera_time()

        self.base_calibrator = BaseCalibrator(self.camera, 
                                              self.tag, 
                                              tag_gps_angle_threshold=self.tag_gps_angle_threshold)


        return self
    
    def test_get_base_position_returns_close_to_actual_base_position(self):
        cbp = self.base_calibrator.get_base_position()
        abp = self.camera.get_actual_position()

        self.assertEqual(type(cbp), tuple)
        self.assertEqual(type(abp), tuple)

        for i,_ in enumerate(cbp):
            self.assertAlmostEqual(cbp[i], abp[i], places=5)

    def test_get_intersection_points_returns_a_multipoint(self):
        points = self.base_calibrator._get_points_where_error_circle_intersections_intersect_each_other()
        self.assertGreater(len(points), 0)
        self.assertEqual(type(points), MultiPoint)

    def test_all_error_circle_intersections_interesect_each_other(self):
        intersections = self.base_calibrator._get_all_error_circle_intersections()
        for a in intersections:
            for b in intersections:
                self.assertTrue(a.intersects(b))

    def test_get_all_error_circle_intersections_gets_a_list_of_linestrings(self):
        intersections = self.base_calibrator._get_all_error_circle_intersections()
        self.assertGreater(len(intersections), 0)
        for isect in intersections:
            self.assertEqual(type(isect), LineString)
    
    def test_get_all_circumcircle_objects_returns_circumcircle_objects_for_the_tag(self):
        ccs = self.base_calibrator._get_all_circumcircle_objects()
        self.assertGreater(len(ccs), 0)
        for cc in ccs:
            self.assertEqual(type(cc), Circumcircles)
        
    def visualize(self):
        self.boundary_renderer = BoundaryRenderer(self.boundary)
        self.camera_renderer = CameraRenderer(self.camera)
        self.viewable_objects_renderer = ViewableObjectsRenderer(self.viewable_objects, computer_vision=self.camera.get_computer_vision())
        self.image_renderer = ImageRenderer(self.camera.get_image_generator())
        self.image_renderer.set_computer_vision(self.camera.get_computer_vision())
        self.circumcircle_renderer = CircumcircleRenderer(self.base_calibrator.get_object_motion_analyzer())

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