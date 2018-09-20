import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
from tk_canvas_renderers.tk_renderer import TKRenderer

class ElementRenderer:
    def __init__(self, **kargs):
        self.tk_renderer = TKRenderer()
        self.moving_rendered_elements = []
        self.stationary_rendered_elements = []

    def render(self, timestamp=None, **kargs):
        if timestamp == None:
            self.render_stationary_elements()
        else:
            self.render_moving_elements(timestamp)

        return self
    
    # implement in child class
    def render_stationary_elements(self):
        pass  

    # implement in child class
    def render_moving_elements(self, timestamp):
        pass  

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
    
    def render_stationary_elements(self):
        self.delete_stationary_rendered_elements()
        self.stationary_rendered_elements.append(self.tk_renderer.create_polygon(self.boundary.exterior.coords, fill='', outline='orange'))

class ViewableObjectsRenderer(ElementRenderer):
    def __init__(self, viewable_objects=[], computer_vision=None, **kargs):
        self.computer_vision = computer_vision
        self.viewable_objects = viewable_objects
        self.detected_color = 'green'
        self.undetected_color = 'black'
        self.tag_color = 'red'
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

    def render_moving_elements(self, timestamp):
        self.delete_moving_rendered_elements()
        for obj in self.viewable_objects:
            self.render_viewable_object(obj, timestamp)
        
    def render_viewable_object(self, obj, timestamp):
        self.moving_rendered_elements.append(self.get_dot(      obj.get_position_at_timestamp(timestamp), obj, timestamp))

        self.moving_rendered_elements.append(self.get_dot_label(obj.get_position_at_timestamp(timestamp), obj, timestamp))

    def get_dot_label(self, coords, obj, timestamp):
        return self.tk_renderer.create_dot_label(coords,
                                                 text=self.cv_id_for_object(obj, timestamp),
                                                 fill=self.color(obj, timestamp))
    def get_dot(self, coords, obj, timestamp):
        return self.tk_renderer.create_dot(coords,
                                           outline=self.color(obj, timestamp),
                                           fill=self.color(obj,timestamp)) 

    def cv_id_for_object(self, obj, timestamp):
        if obj.get_is_tag():
            return 'tag'
        elif self.computer_vision == None:
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
        if obj.get_is_tag():
            return self.tag_color
        elif self.is_detected_by_cv(obj, timestamp):
            return self.detected_color
        else:
            return self.undetected_color


class ImageRenderer(ViewableObjectsRenderer):

    def __init__(self, image_generator, **kargs):
        self.image_generator = image_generator
        self.y_of_line = 50
        self.x_of_line = 50
        self.origin =  (self.x_of_line, self.y_of_line)
        self.image_width = self.image_generator.get_image_width()
        self.center_x_of_line = int(self.x_of_line + self.image_width / 2)
        self.x_for_all_inview_objects_for_all_camera_time = self.image_generator.get_x_for_all_inview_objects_for_all_camera_time()
        super().__init__(**kargs)

    def get_image_width(self):
        return self.image_width
        
    def render_stationary_elements(self):
        self.delete_stationary_rendered_elements()
        self.render_line()
    
    def render_moving_elements(self, timestamp):
        self.delete_moving_rendered_elements()
        self.render_inview_objects(timestamp)

    def render_inview_objects(self, timestamp):
        for obj in self.x_for_all_inview_objects_for_all_camera_time[timestamp].keys():
            self.render_inview_object(obj, timestamp)
    
    def render_inview_object(self, obj, timestamp):
        x = self.x_for_all_inview_objects_for_all_camera_time[timestamp][obj]
        coords = (self.get_rendered_x_for_x(x), self.y_of_line)
        self.moving_rendered_elements.append(      self.get_dot(coords, obj, timestamp))
        self.moving_rendered_elements.append(self.get_dot_label(coords, obj, timestamp))

    def get_rendered_x_for_x(self, x):
        return self.center_x_of_line - x  

    def render_line(self):
        self.stationary_rendered_elements.append(self.tk_renderer.create_line([self.origin, 
                                                                              (self.x_of_line + self.image_width, self.y_of_line)] ))

class CameraRenderer(ElementRenderer):

    def __init__(self, camera, **kargs):
        self.camera = camera
        self.tk_renderer = TKRenderer()
        self.camera_color = 'green'
        self.camera_gps_color = 'red'
        self.gps_err_color = 'red'
        self.view_triangle_color = '#FEFAED'
        super().__init__(**kargs)

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


class CircumcircleRenderer(ElementRenderer):

    def __init__(self, circumcirlcle_analyzer, **kargs):
        self.circumcircle_analyzer = circumcirlcle_analyzer
        self.frames = circumcirlcle_analyzer.get_frames()
        super().__init__(**kargs)
    
    def render_stationary_elements(self):
        self.delete_stationary_rendered_elements()
        for frame in self.frames:
            p1 = self.circumcircle_analyzer.get_tag_position_analyzer().get_early_position(frame)
            p2 = self.circumcircle_analyzer.get_tag_position_analyzer().get_late_position(frame)
            tag = self.circumcircle_analyzer.get_tag(frame)
            if p1 != None and p2 != None and tag != None:
                self.stationary_rendered_elements.append(self.tk_renderer.create_dot(p1))
                self.stationary_rendered_elements.append(self.tk_renderer.create_dot(p2))

                cc = self.circumcircle_analyzer.get_circumcircles(frame)[tag]
                c1_center = cc.get_circumcenters()[0]
                c2_center = cc.get_circumcenters()[1]
                cc_radius = cc.get_circumradius()
                self.stationary_rendered_elements.append(self.tk_renderer.create_circle_with_center_and_radius(c1_center, cc_radius))
                self.stationary_rendered_elements.append(self.tk_renderer.create_circle_with_center_and_radius(c2_center, cc_radius))