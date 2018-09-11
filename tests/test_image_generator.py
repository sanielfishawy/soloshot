import unittest, math, sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
from image_generator import ImageGenerator
from camera import Camera
from computer_vision import ComputerVision
from object_universe import ObjectUniverse
from viewable_object import StationaryObject

class TestImageGenerator(unittest.TestCase):

    def setUp(self):
        self.num_timestamps = 10
        self.fov = math.pi / 2
        self.image_width = 1000
        self.object_universe = ObjectUniverse(num_timestamps=self.num_timestamps)
        self.camera = Camera()
        
        self.camera.set_actual_position((1,1)).\
                    set_fov_rad(self.fov).\
                    set_num_timestamps(self.num_timestamps).\
                    set_range(50000)
        
        for timestamp in range(self.camera.get_num_timestamps()):
            self.camera.set_state_of_pan_motor_angle_at_timestamp_rad(math.pi / 4, timestamp)
        
        self.cv = ComputerVision()
        self.image_generator = ImageGenerator(image_width=self.image_width)
        self.camera.set_computer_vision(self.cv).\
                    set_image_generator(self.image_generator)

        self.viewable_objects = [ 
                                StationaryObject( (2, 1 + math.tan(math.pi / 8)) ),
                                StationaryObject( (1 + math.tan(math.pi / 8), 2)  ),
                                StationaryObject( (10000, 1.1) ),
                                StationaryObject( (1.1, 10000) ),
                                ]
        self.object_universe.add_viewable_objects(self.viewable_objects)
        self.object_universe.add_camera(self.camera)

        self.d = self.image_width / ( 2 * math.tan(self.fov / 2) )
        self.theta = math.pi / 8

    def test_d_calculation_for_image_generator(self):
        self.camera.get_image_generator().get_x_for_all_inview_objects_for_all_camera_time()
        self.assertEqual(self.d, self.image_generator.d)
        
    def test_theta_calculation_for_image_generator(self):
        self.camera.get_image_generator().get_x_for_all_inview_objects_for_all_camera_time()
        self.assertAlmostEqual(-self.theta, self.image_generator._get_theta_rad(self.viewable_objects[0], 0))
        self.assertAlmostEqual(self.theta, self.image_generator._get_theta_rad(self.viewable_objects[1], 0))

    def test_get_x_for_all_inview_objects_for_all_camera_time(self):

        r = self.image_generator.get_x_for_all_inview_objects_for_all_camera_time()

        for timestamp in range(self.camera.get_num_timestamps()):
            self.assertAlmostEqual(r[timestamp][self.viewable_objects[0]], - self.d * math.tan(math.pi/8))
            self.assertAlmostEqual(r[timestamp][self.viewable_objects[1]],   self.d * math.tan(math.pi/8))
        
    def test_get_x_for_distant_objects_at_edge_of_view_remain_in_image_width(self):

        r = self.image_generator.get_x_for_all_inview_objects_for_all_camera_time()

        for obj in self.viewable_objects:
            x = r[0][obj]
            self.assertLess(abs(x), self.image_width / 2)

# These tests were created when tracking down a bug relating to initialization of the calculation for d
# before camera fov is finalized. 
class TestImageGeneratorZeroAngle(unittest.TestCase):

    def setUp(self):
        self.num_timestamps = 2
        self.fov = math.pi / 2
        self.object_universe = ObjectUniverse(num_timestamps=self.num_timestamps)

        self.camera = Camera()
        
        self.camera.set_fov_rad(math.pi / 2).\
                    set_actual_position((100,400)).\
                    set_gps_position((100,410)).\
                    set_gps_max_error(12).\
                    set_num_timestamps(self.num_timestamps)

        for timestamp in range(self.num_timestamps):
            self.camera.set_state_of_pan_motor_angle_at_timestamp(0, timestamp)

        self.viewable_objects = [ 
                                StationaryObject( (300, 599) ),
                                StationaryObject( (300, 201) ),
                                ]
        self.object_universe.add_viewable_objects(self.viewable_objects)
        self.object_universe.add_camera(self.camera)


    def test_fov(self):
        self.camera.image_generator.get_x_for_all_inview_objects_for_all_camera_time()
        self.assertEqual(self.camera.get_image_generator().fov, math.pi / 2)

    def test_d(self):
        self.camera.image_generator.get_x_for_all_inview_objects_for_all_camera_time()
        self.assertAlmostEqual(self.camera.get_image_generator().d, 320)

    def test_get_x_remain_in_image_width(self):
        r = self.camera.get_image_generator().get_x_for_all_inview_objects_for_all_camera_time()

        for obj in self.viewable_objects:
            x = r[0][obj]
            self.assertLess(abs(x), self.camera.get_image_generator().get_image_width() / 2)

    def test_image_width_default(self):
        self.assertEqual(self.camera.get_image_generator().get_image_width(), 640)
            
if __name__ == '__main__':
    unittest.main()