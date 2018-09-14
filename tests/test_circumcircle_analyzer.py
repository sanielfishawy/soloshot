import sys, unittest, math
sys.path.insert(0, '/Users/sani/dev/soloshot')
from object_universe import ObjectUniverse
from camera import Camera
from image_analyzer import ImageAnalyzer
from circumcircle_analyzer import CircumcircleAnalyzer
from viewable_object import RandomlyMovingObject, RandomlyMovingTag
from boundary import Boundary

from tk_canvas_renderers.element_renderers import BoundaryRenderer, CameraRenderer, ViewableObjectsRenderer, ImageRenderer, TKRenderer
from tk_canvas_renderers.animator import Animator

class TestCircumcircleAnalyzer(unittest.TestCase):

    def setUp(self):
        self.num_timestamps = 100

        self.object_universe = ObjectUniverse(num_timestamps=self.num_timestamps)

        self.camera = Camera()
        self.camera.set_actual_position((100, 400)).\
                    set_gps_position((100,380)).\
                    set_gps_max_error(20).\
                    set_fov_rad(math.pi/2)
    
        self.boundary = Boundary([(220,300), (420,100), (420,700), (220, 500)])
        
        self.tag = RandomlyMovingTag(boundary=self.boundary)
        self.r_obj = RandomlyMovingObject(boundary=self.boundary)
        self.viewable_objects = [self.tag, self.r_obj]

        self.object_universe.add_camera(self.camera).\
                             add_viewable_objects(self.viewable_objects)

        for timestamp in range(self.num_timestamps):
            self.camera.set_state_of_pan_motor_angle_at_timestamp(0, timestamp)
        
        self.camera.get_computer_vision().set_cv_ids_for_all_camera_time()

        self.image_analyzer = ImageAnalyzer(self.camera)
        
        self.circumcircle_analyzer = CircumcircleAnalyzer(self.camera, self.tag)

    def test_circum(self):
        frames = self.circumcircle_analyzer.get_analyzed_frames()
        pass

    def dont_test_visually(self):
        self.boundary_renderer = BoundaryRenderer(self.boundary)
        self.camera_renderer = CameraRenderer(self.camera)
        self.viewable_objects_renderer = ViewableObjectsRenderer(self.viewable_objects, computer_vision=self.camera.get_computer_vision())
        self.image_renderer = ImageRenderer(self.camera.get_image_generator())

        self.renderers = [
                            self.camera_renderer,
                            self.viewable_objects_renderer,
                            self.boundary_renderer,
                            self.image_renderer,
        ]

        self.animator = Animator(element_renderers=self.renderers, num_timestamps=self.num_timestamps, seconds_per_timestamp=0.2)

        TKRenderer().set_canvas_height(900).\
                     set_canvas_width(1000).\
                     set_scale(1).\
                     set_mouse_click_callback(self.animator.play).\
                     start_tk_event_loop()

if __name__ == '__main__':
    unittest.main()