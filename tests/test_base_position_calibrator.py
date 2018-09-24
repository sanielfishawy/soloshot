import sys, math, unittest
sys.path.insert(0, '/Users/sani/dev/soloshot')
from shapely.geometry import LineString, Point, MultiPoint

from base_position_calibrator import BasePositionCalibrator
from object_universe import ObjectUniverse
from camera import Camera
from viewable_object import RandomlyMovingObject, RandomlyMovingTag
from boundary import Boundary
from object_motion_analyzer import Circumcircles

from tk_canvas_renderers.render_orchestrator import RenderOrchestrator

class TestBasePositionCalibrator(unittest.TestCase):

    def setUp(self, num_randomly_moving_objects=10, tag_gps_angle_threshold=6):
        self.num_randomly_moving_objects = num_randomly_moving_objects

        self.num_timestamps = 50
        self.tag_gps_angle_threshold = math.radians(tag_gps_angle_threshold)

        self.object_universe = ObjectUniverse(num_timestamps=self.num_timestamps)

        self.camera = Camera()
        self.camera.set_actual_position((100, 400)).\
                    set_gps_position((100,380)).\
                    set_gps_max_error(25).\
                    set_fov_rad(math.pi/2)
    
        self.boundary = Boundary([(220,300), (420,100), (420,700), (220, 500)])
        
        self.tag = RandomlyMovingTag(boundary=self.boundary)
        self.r_objs = []
        for _ in range(self.num_randomly_moving_objects):
            self.r_objs.append(RandomlyMovingObject(boundary=self.boundary))
        
        self.viewable_objects = [self.tag] + self.r_objs

        self.object_universe.add_camera(self.camera).\
                             add_viewable_objects(self.viewable_objects)

        for timestamp in range(self.num_timestamps):
            self.camera.set_state_of_pan_motor_angle_at_timestamp(0, timestamp)
        
        self.camera.get_computer_vision().set_cv_ids_for_all_camera_time()

        self.base_position_calibrator = BasePositionCalibrator(self.camera, 
                                              self.tag, 
                                              tag_gps_angle_threshold=self.tag_gps_angle_threshold)


        return self
    
    def test_get_all_circumcircle_objects_gets_only_cc_objects(self):
        # Wrote this test while tracking down a bug which seems to be in ObjectPositionAnalyzer but which I discovered
        # when testing BaseAngleCalibrator. But I cant reproduce it here or in TestObjectMotionAnalyzer
        ccs = self.base_position_calibrator._get_all_circumcircle_objects()
        self.assertGreater(len(ccs), 0)
        for cc in ccs:
            self.assertEqual(type(cc), Circumcircles)


    def test_tag_candidate_is_always_the_tag(self):
        self.assertEqual(self.tag, self.base_position_calibrator.get_tag_candidate())

    def test_get_base_position_returns_close_to_actual_base_position(self):
        cbp = self.base_position_calibrator.get_base_position()
        abp = self.camera.get_actual_position()

        self.assertEqual(type(cbp), tuple)
        self.assertEqual(type(abp), tuple)

        for i,_ in enumerate(cbp):
            self.assertAlmostEqual(cbp[i], abp[i], places=4)

    def test_get_intersection_points_returns_a_multipoint(self):
        points = self.base_position_calibrator._get_points_where_error_circle_intersections_intersect_each_other()
        self.assertGreater(len(points), 0)
        self.assertEqual(type(points), MultiPoint)

    def test_all_error_circle_intersections_interesect_each_other(self):
        intersections = self.base_position_calibrator.get_all_error_circle_intersections()
        for a in intersections:
            for b in intersections:
                self.assertTrue(a.intersects(b))

    def test_get_all_error_circle_intersections_gets_a_list_of_linestrings(self):
        intersections = self.base_position_calibrator.get_all_error_circle_intersections()
        self.assertGreater(len(intersections), 0)
        for isect in intersections:
            self.assertEqual(type(isect), LineString)
    
    def test_get_all_circumcircle_objects_returns_circumcircle_objects_for_the_tag(self):
        ccs = self.base_position_calibrator._get_all_circumcircle_objects()
        self.assertGreater(len(ccs), 0)
        for cc in ccs:
            self.assertEqual(type(cc), Circumcircles)
        
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