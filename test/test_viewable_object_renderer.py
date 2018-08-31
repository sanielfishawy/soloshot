import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
import unittest
from tk_canvas_renderers.tk_renderer import TKRenderer
from tk_canvas_renderers.element_renderers import ViewableObjectsRenderer
from viewable_object import StationaryObject

class TestViewableObjectRenderer(unittest.TestCase):

    def setUp(self):
        self.tk_renderer = TKRenderer(scale=2)
        self.stationary_object = StationaryObject((100,100))
        self.viewable_objects = [
                                 self.stationary_object
                                ]
        self.viewable_object_renderer = ViewableObjectsRenderer(viewable_objects=self.viewable_objects)
    
    def test_visually(self):
        self.viewable_object_renderer.render(0)
        self.tk_renderer.start_tk_event_loop()
    
if __name__ == '__main__':
    unittest.main()