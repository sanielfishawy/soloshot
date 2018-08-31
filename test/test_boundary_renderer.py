import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
import unittest
from tk_canvas_renderers.tk_renderer import TKRenderer
from tk_canvas_renderers.element_renderers import BoundaryRenderer
from boundary import Boundary

class TestBoundaryRenderer(unittest.TestCase):

    def setUp(self):
        self.canvas_width = 2000
        self.canvas_height = 1000
        self.bounary_points = [(100,100), (300,100), (300,200), (100,200)]
        self.tk_renderer = TKRenderer(scale=2, canvas_width=self.canvas_width, canvas_height=self.canvas_height)
        self.boundary = Boundary(self.bounary_points)
        self.boundary_renderer = BoundaryRenderer(self.boundary)


    def test_params_are_passed_to_tk_renderer_singleton(self):
        self.assertEqual(self.tk_renderer.canvas_width, self.canvas_width)
        self.assertEqual(self.tk_renderer.canvas_height, self.canvas_height)

    def test_visually(self):
        self.boundary_renderer.render()
        self.tk_renderer.start_tk_event_loop()


if __name__ == '__main__':
    unittest.main()