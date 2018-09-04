import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
import unittest
from tk_canvas_renderers.tk_renderer import TKRenderer
from tk_canvas_renderers.element_renderers import ViewableObjectsRenderer, BoundaryRenderer
from viewable_object import RandomlyMovingObject
from boundary import Boundary
from tk_canvas_renderers.animator import Animator

class TestMovingObjectRenderer(unittest.TestCase):

    def setUp(self):
        self.num_timestamps = 1000
        self.tk_renderer = TKRenderer(canvas_width=800, canvas_height=700)
        self.boundary = Boundary([(100,100), (300,100), (300,200), (100,200)])
        self.boundary_renderer = BoundaryRenderer(self.boundary)
        self.random_moving_objects = [
                                       RandomlyMovingObject(boundary=self.boundary, num_timestamps=self.num_timestamps),
                                       RandomlyMovingObject(boundary=self.boundary, num_timestamps=self.num_timestamps)
                                     ]
        self.viewable_objects_renderer = ViewableObjectsRenderer(viewable_objects=self.random_moving_objects)
        self.animator = Animator(num_timestamps=self.num_timestamps, seconds_per_timestamp=0.2)
        self.animator.add_element_renderers([self.viewable_objects_renderer,
                                             self.boundary_renderer] )
        self.tk_renderer.set_mouse_click_callback(self.animator.play)
        return self
    
    def visualize(self):
        self.tk_renderer.start_tk_event_loop()
        
if __name__ == '__main__':
    unittest.main()

