import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
import math, unittest
from camera import Camera
from object_universe import ObjectUniverse
from viewable_object import ViewableObject
from image_analyzer import ImageAnalyzer

class TestImageAnalyzer(unittest.TestCase):

    def setUp(self):
        self.num_timestamps = 7
        self.fov_deg = 92
        self.fov_rad = math.radians(self.fov_deg)
        self.object_universe = ObjectUniverse(num_timestamps=self.num_timestamps)

        self.camera = Camera()
        self.camera.set_fov_deg(self.fov_deg).set_actual_position((0,0))
        for timestamp in range(self.num_timestamps):
            self.camera.set_state_of_pan_motor_angle_at_timestamp(0, timestamp)
        
        self.viewable_object = ViewableObject()

        self.object_universe.add_camera(self.camera).\
                             add_viewable_objects(self.viewable_object)
        
        self.angles = [
                        -math.pi/4,
                        -math.pi/8,
                         math.pi/8,
                         math.pi/4,
                      ]

        self.image_width = self.camera.get_image_generator().get_image_width()
        self.d = self.image_width / 2 / math.tan(self.fov_rad / 2)
        
        self.x_s = [ self.d * math.tan(a) for a in self.angles ]

        self.positions = [ (self.d, x) for x in self.x_s ]

        self.sequence = [0, 1, 0, 2, 3, 2, 1]

        for timestamp, s in enumerate(self.sequence):
            self.viewable_object.set_position_at_timestamp(self.positions[s], timestamp)

        self.subtended_angles = [
                                 math.pi / 8,
                                -math.pi / 8,
                             3 * math.pi / 8,
                                 math.pi / 8,
                                -math.pi / 8,
                                -math.pi / 4,
                                ]

        self.image_analyzer = ImageAnalyzer(self.camera)
        self.image_analyzer.set_images(self.camera.get_image_generator().get_x_for_all_inview_objects_for_all_camera_time())

    def test_angles(self):

        for i, _ in enumerate(self.subtended_angles):
            a_s = self.image_analyzer.get_subtended_angles_for_all_objects(i, i+1)
            self.assertAlmostEqual(a_s[self.viewable_object], self.subtended_angles[i])
        


if __name__ == '__main__':
    unittest.main()
