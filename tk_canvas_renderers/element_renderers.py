import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
from tk_canvas_renderers.tk_renderer import TKRenderer

class ElementRenderer:
    def __init__(self, **kargs):
        self.tk_renderer = TKRenderer()
        self.rendered_elements = []

    def delete_all_rendered_elements(self):
        self.tk_renderer.delete_elements(self.rendered_elements)
        self.rendered_elements = []

class BoundaryRenderer(ElementRenderer):
    def __init__(self, boundary, **kargs):
        self.tk_renderer = TKRenderer()
        self.boundary = boundary
        super().__init__(**kargs)
    
    def render(self, **kargs):
        self.delete_all_rendered_elements()
        self.rendered_elements.append(self.tk_renderer.create_polygon(self.boundary.exterior.coords, fill='', outline='orange'))

class ViewableObjectsRenderer(ElementRenderer):
    def __init__(self, viewable_objects=[], computer_vision=None, **kargs):
        self.computer_vision = computer_vision
        self.viewable_objects = viewable_objects
        self.detected_color = 'green'
        self.undetected_color = 'black'
        super().__init__(**kargs)

    def set_computer_vision(self, cv):
        self.computer_vision = cv
        return self

    def get_computer_vision(self):
        return self.computer_vision
    
    def set_viewable_objects(self, vo_s):
        self.viewable_objects = vo_s
        return self

    def get_viewable_objects(self):
        return self.viewable_objects

    def render(self, timestamp=0, **kargs):
        self.delete_all_rendered_elements()
        for obj in self.viewable_objects:
            self.render_viewable_object(obj, timestamp)
        
    def render_viewable_object(self, obj, timestamp):
        self.rendered_elements.append(self.tk_renderer.create_dot(obj.get_position_at_timestamp(timestamp),
                                                                  outline=self.color(obj, timestamp),
                                                                  fill=self.color(obj,timestamp)))

        self.rendered_elements.append(self.tk_renderer.create_dot_label(obj.get_position_at_timestamp(timestamp),
                                                                        text=self.cv_id_for_object(obj, timestamp),
                                                                        fill=self.color(obj, timestamp)))

    def cv_id_for_object(self, obj, timestamp):
        if self.computer_vision == None:
            return '?'
        else:
            return self.computer_vision.get_cv_id_for_obj_at_timestamp(obj, timestamp)

    def is_detected_by_cv(self, obj, timestamp):
        if self.computer_vision == None:
            return False
        elif self.computer_vision.get_cv_id_for_obj_at_timestamp(obj, timestamp) == None:
            return False
        else:
            return True

    def color(self, obj, timestamp):
        if self.is_detected_by_cv(obj, timestamp):
            return self.detected_color
        else:
            return self.undetected_color