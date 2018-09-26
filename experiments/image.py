import sys, os
sys.path.insert(0, os.getcwd())

from tk_canvas_renderers.tk_renderer import TKRenderer
from tk_canvas_renderers.element_renderers import PhotoRenderer
from tk_canvas_renderers.animator import Animator
import PIL



photo_url = os.getcwd() + '/data/images/will.jpg'
image = PIL.Image.open(photo_url)
image_r = image.resize((400,300))
image_renderer = PhotoRenderer(image_r)
animator = Animator([image_renderer])
TKRenderer().set_canvas_height(500).\
                set_canvas_width(1200).\
                set_scale(1).\
                set_mouse_click_callback(animator.play)

TKRenderer().start_tk_event_loop()


 #     self.boundary_renderer = BoundaryRenderer(self.boundary)

    #     self.renderers = [
    #                         self.camera_renderer,
    #                         self.viewable_objects_renderer,
    #                         self.boundary_renderer
    #     ]

    #     self.animator = Animator(element_renderers=self.renderers, num_timestamps=self.num_timestamps, seconds_per_timestamp=0.2)
    #     TKRenderer().set_canvas_height(800).\
    #                  set_canvas_width(900).\
    #                  set_scale(1).\
    #                  set_mouse_click_callback(self.animator.play)

    # def run(self):
    #     TKRenderer().start_tk_event_loop()