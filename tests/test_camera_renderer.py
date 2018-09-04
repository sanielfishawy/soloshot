import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
import unittest
from camera import Camera
from tk_canvas_renderers.element_renderers import CameraRenderer
from tk_canvas_renderers.animator import Animator
from tk_canvas_renderers.tk_renderer import TKRenderer

class TestCameraRenderer(unittest.TestCase):

    def setUp(self):
        self.num_timestamps = 180
        self.tk_renderer = TKRenderer(canvas_width=1200, canvas_height=800, scale=2)         

        self.camera = Camera()
        self.camera.set_actual_position((200,200)).\
                    set_gps_max_error(10).\
                    set_num_timestamps(self.num_timestamps).\
                    set_gps_position((200, 210))
        for timestamp in range(self.num_timestamps):
            self.camera.set_state_of_pan_motor_angle_at_timestamp(timestamp*2, timestamp)

        self.camera_renderer = CameraRenderer(self.camera)
        self.camera_renderer.render()
        self.animator = Animator([self.camera_renderer], num_timestamps=self.num_timestamps, seconds_per_timestamp=0.05)
        self.tk_renderer.set_mouse_click_callback(self.animator.play)
        return self

    def visualize(self):
        self.tk_renderer.start_tk_event_loop()

if __name__ == '__main__':
    unittest.main()