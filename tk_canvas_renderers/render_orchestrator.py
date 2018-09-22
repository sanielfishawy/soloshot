import sys
sys.path.insert(0, '/Users/Sani/dev/soloshot')

import tk_canvas_renderers.element_renderers as ER
from tk_canvas_renderers.animator import Animator
from tk_canvas_renderers.tk_renderer import TKRenderer

from boundary import Boundary
from object_universe import ObjectUniverse
from camera import Camera
from viewable_object import ViewableObjects
from image_generator import ImageGenerator
from base_position_calibrator import BasePositionCalibrator
from object_motion_analyzer import ObjectMotionAnalyzer

class RenderOrchestrator:

    def __init__(self, num_timestamps, renderable_objects, seconds_per_timestamp=0.2, canvas_width=1000, canvas_height=900, scale=1):
        self.num_timestamps = num_timestamps
        self.seconds_per_timestamp = seconds_per_timestamp
        self._renderable_objects = renderable_objects
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.scale = scale
    
        self._element_renderers = {}
        self.object_stats_processor = None
    
    def _add_renderers_for_objects(self):
        for r_o in self._renderable_objects:
            self._add_renders_for_object(r_o)
        return self
    
    def _add_renders_for_object(self, renderable_object):
        if type(renderable_object) == Boundary:
            self._add_renderer_for_object(renderable_object, ER.BoundaryRenderer(renderable_object))

        elif type(renderable_object) == ObjectUniverse:
            camera = renderable_object.get_camera()
            viewable_objects = renderable_object.get_viewable_objects_as_viewable_objects_class()

            self._add_camera_renderer(camera)

            if type(camera) == Camera:
                computer_vision = camera.get_computer_vision()
                image_generator = camera.get_image_generator()
            else:
                computer_vision = None
                image_generator = None

            self._add_viewable_objects_renderer(viewable_objects, computer_vision)
            self._add_image_render(image_generator, computer_vision)
        
        elif type(renderable_object) == BasePositionCalibrator:
            self._add_renderer_for_object(renderable_object, ER.BasePositionCalibratorRenderer(renderable_object))
            self.object_stats_processor = renderable_object.get_object_stats_processor()
            self._set_object_stats_processor_in_image_renderer()
            
        elif type(renderable_object) == Camera:
            raise "Pass ObjectUniverse with camera rather than Camera directly"
    
        elif type(renderable_object) == list or type(renderable_object) == ViewableObjects:
            raise "Trying to pass in ViewableObjects? use ObjectUniverse rather than passing them directly"
    
    def _set_object_stats_processor_in_image_renderer(self):
        if type(ImageGenerator()) in self._element_renderers:
            self._element_renderers[type(ImageGenerator())].set_object_stats_processor(self.object_stats_processor)

    def _add_renderer_for_object(self, renderable_object, renderer):
        self._element_renderers[type(renderable_object)] = renderer
        return self

    def _add_camera_renderer(self, camera):
        if type(camera) == Camera:
            self._add_renderer_for_object(camera, ER.CameraRenderer(camera))

    def _add_viewable_objects_renderer(self, viewable_objects, computer_vision):
        if type(viewable_objects) == None:
            return

        if type(viewable_objects) != ViewableObjects:
            raise "you must use ViewableObjects class to pass in ViewableObjects"
        
        self._add_renderer_for_object(viewable_objects, 
                                      ER.ViewableObjectsRenderer(viewable_objects=viewable_objects.get_viewable_objects(),
                                                                 computer_vision=computer_vision))
    def _add_image_render(self, image_generator, computer_vision):
        if type(image_generator) == ImageGenerator:
            self._add_renderer_for_object(image_generator, ER.ImageRenderer(image_generator, 
                                                                            computer_vision=computer_vision,
                                                                            object_stats_processor=self.object_stats_processor))

    def _get_renderers(self):
        return [self._element_renderers[key] for key in self._element_renderers]

    def _set_animator(self):
        self.animator = Animator(element_renderers=self._get_renderers(), 
                                 num_timestamps=self.num_timestamps,
                                 seconds_per_timestamp=self.seconds_per_timestamp)
    
    def run(self):
        self._add_renderers_for_objects()
        self._set_animator()
        TKRenderer().set_canvas_height(self.canvas_height).\
                     set_canvas_width(self.canvas_width).\
                     set_scale(self.scale).\
                     set_mouse_click_callback(self.animator.play).\
                     start_tk_event_loop()