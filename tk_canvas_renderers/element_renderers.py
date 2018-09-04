import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
from tk_canvas_renderers.tk_renderer import TKRenderer

class ElementRenderer:
    def __init__(self, **kargs):
        self.tk_renderer = TKRenderer()
        self.moving_rendered_elements = []
        self.stationary_rendered_elements = []

    def delete_moving_rendered_elements(self):
        self.tk_renderer.delete_elements(self.moving_rendered_elements)
        self.moving_rendered_elements = []
        return self
    
    def delete_stationary_rendered_elements(self):
        self.tk_renderer.delete_elements(self.stationary_rendered_elements)
        return self

    def delete_all_rendered_elements(self):
        self.delete_moving_rendered_elements()
        self.delete_stationary_rendered_elements()

class BoundaryRenderer(ElementRenderer):
    def __init__(self, boundary, **kargs):
        self.tk_renderer = TKRenderer()
        self.boundary = boundary
        super().__init__(**kargs)
    
    def render(self, **kargs):
        self.delete_moving_rendered_elements()
        self.moving_rendered_elements.append(self.tk_renderer.create_polygon(self.boundary.exterior.coords, fill='', outline='orange'))

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
        self.delete_moving_rendered_elements()
        for obj in self.viewable_objects:
            self.render_viewable_object(obj, timestamp)
        
    def render_viewable_object(self, obj, timestamp):
        self.moving_rendered_elements.append(self.tk_renderer.create_dot(obj.get_position_at_timestamp(timestamp),
                                                                  outline=self.color(obj, timestamp),
                                                                  fill=self.color(obj,timestamp)))

        self.moving_rendered_elements.append(self.tk_renderer.create_dot_label(obj.get_position_at_timestamp(timestamp),
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

class CameraRenderer(ElementRenderer):

    def __init__(self, camera, **kargs):
        self.camera = camera
        self.tk_renderer = TKRenderer()
        self.camera_color = 'green'
        self.camera_gps_color = 'red'
        self.gps_err_color = 'red'
        self.view_triangle_color = '#FEFAED'
        super().__init__(**kargs)

    def render(self, timestamp=None, **kargs):
        if timestamp == None:
            self.render_stationary_elements()
        else:
            self.render_moving_elements(timestamp)

        return self

    def render_stationary_elements(self):
        self.delete_stationary_rendered_elements()
        self.render_camera_gps()
        self.render_gps_error_circle()
        self.render_camera()
        return self

    def render_moving_elements(self, timestamp):
        self.delete_moving_rendered_elements()
        self.render_view_triangle(timestamp)
        return self

    def render_camera(self):
        pos = self.camera.get_actual_position()
        text = 'c' + str(pos)
        self.stationary_rendered_elements.append(
            self.tk_renderer.create_dot(pos, fill=self.camera_color, 
                                             outline=self.camera_color)
        )
        self.stationary_rendered_elements.append(
            self.tk_renderer.create_dot_label(pos, text=text,
                                                   fill=self.camera_color)
        )
        return self

    def render_camera_gps(self):
        pos = self.camera.get_gps_position()
        label_text = 'gps' + str(self.camera.get_gps_position())
        self.stationary_rendered_elements.append(self.tk_renderer.create_dot(pos, 
                                                 outline=self.camera_gps_color, 
                                                 fill=self.camera_gps_color))
        self.stationary_rendered_elements.append(self.tk_renderer.create_dot_label(pos, 
                                                 text=label_text,
                                                 fill=self.camera_gps_color))                                                
        return self                                                

    def render_gps_error_circle(self):
        err = self.camera.get_gps_max_error()
        self.stationary_rendered_elements.append(
             self.tk_renderer.create_circle_with_center_and_radius(self.camera.get_gps_position(), 
                                                                   err,
                                                                   outline=self.gps_err_color))
        return self

    def render_view_triangle(self, timestamp):
        vt = self.camera.get_view_triangle(timestamp).exterior.coords
        rvt = self.tk_renderer.create_polygon(vt, fill=self.view_triangle_color, 
                                                  outline=self.view_triangle_color)

        self.tk_renderer.lower_element(rvt)
        self.moving_rendered_elements.append(rvt)
        return self