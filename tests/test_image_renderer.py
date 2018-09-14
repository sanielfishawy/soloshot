import sys, unittest, math
sys.path.insert(0, '/Users/sani/dev/soloshot')

from tk_canvas_renderers.tk_renderer import TKRenderer
from tk_canvas_renderers.element_renderers import ImageRenderer, CameraRenderer, ViewableObjectsRenderer, ImageRenderer, BoundaryRenderer
from image_generator import ImageGenerator
from camera import Camera
from computer_vision import ComputerVision
from object_universe import ObjectUniverse
from viewable_object import StationaryObject, RandomlyMovingObject, RandomlyMovingTag
from tk_canvas_renderers.animator import Animator
from boundary import Boundary


class TestImageRenderer(unittest.TestCase):

    def setUp(self):
        # Environment
        self.num_timestamps = 100
        self.object_universe = ObjectUniverse(num_timestamps=self.num_timestamps)

        self.camera = Camera()
        self.camera.set_fov_rad(math.pi / 2).\
                    set_actual_position((100,400)).\
                    set_gps_position((100,410)).\
                    set_gps_max_error(12).\
                    set_num_timestamps(self.num_timestamps)
        for timestamp in range(self.num_timestamps):
            self.camera.set_state_of_pan_motor_angle_at_timestamp(0, timestamp)

        self.viewable_objects = []
        for y in range(100, 800, 50):
            self.viewable_objects.append(StationaryObject((301, y))) 

        self.boundary = Boundary([(200,200), (400,200), (400,600), (200,600)])
        for _ in range(0):
            self.viewable_objects.append(RandomlyMovingObject(boundary=self.boundary))
        
        self.viewable_objects.append(RandomlyMovingTag(boundary=self.boundary))

        self.object_universe.add_camera(self.camera).\
                             add_viewable_objects(self.viewable_objects)
    
        self.camera.get_computer_vision().set_cv_ids_for_all_camera_time()
        
        # Render
        self.camera_renderer = CameraRenderer(self.camera)
        self.objects_renderer = ViewableObjectsRenderer(viewable_objects=self.viewable_objects, 
                                                        computer_vision=self.camera.get_computer_vision())
        self.image_renderer = ImageRenderer(self.camera.get_image_generator())                                                
        self.image_renderer.set_computer_vision(self.camera.get_computer_vision())
        self.boundary_renderer = BoundaryRenderer(self.boundary)
        
        self.renderers = [
                            self.camera_renderer,
                            self.objects_renderer,
                            self.image_renderer,
                            self.boundary_renderer,
                         ]

        self.animator = Animator(element_renderers=self.renderers, 
                                 num_timestamps=self.num_timestamps, 
                                 seconds_per_timestamp=0.2)

        TKRenderer().set_canvas_height(800).\
                     set_canvas_width(900).\
                     set_scale(1).\
                     set_mouse_click_callback(self.animator.play)

        return self

    def test_default_image_width_is_640(self):
        self.assertEqual(self.camera.get_image_generator().get_image_width(), 640)
        self.assertEqual(self.image_renderer.get_image_width(), 640)
    
    def test_all_in_view_objects_are_projected_within_image_width(self):
        x_for_all_inview_objects = self.camera.image_generator.get_x_for_all_inview_objects_for_all_camera_time()       

        for x_s in x_for_all_inview_objects:
            for obj in x_s.keys():
                self.assertLess(abs(x_s[obj]), self.image_renderer.get_image_width() / 2)
        

    def visualize(self):
        TKRenderer().start_tk_event_loop()

if __name__ == '__main__':
    unittest.main()