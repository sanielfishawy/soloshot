# pylint: disable=C0413
import sys
import os
sys.path.insert(0, os.getcwd())


from tk_canvas_renderers.tk_renderer import TKRenderer
from base_position_calibrator import BasePositionCalibrator
from object_motion_analyzer import ObjectMotionAnalyzer
from tag_position_analyzer import TagPositionAnalyzer
from object_stats_processor import ObjectsStatsProcessor

class ElementRenderer:
    def __init__(self, **kargs):
        self.tk_renderer = TKRenderer()
        self.moving_rendered_elements = []
        self.stationary_rendered_elements = []

    def render(self, timestamp=None, **kargs):
        if timestamp is None:
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

    def get_dot_label(self, coords, obj, timestamp, **kargs):
        return self.tk_renderer.create_dot_label(coords,
                                                 text=self.cv_id_for_object(obj, timestamp),
                                                 fill=self.color(obj, timestamp),
                                                 **kargs)
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

    def __init__(self, image_generator, object_stats_processor=None, **kargs):
        '''
        :param ImageGenerator image_generator:
        :param ObjectsStatsProcessor object_stats_processor:
        '''
        self.image_generator = image_generator
        self.object_stats_processor = object_stats_processor
        self.y_of_line = 50
        self.x_of_line = 50
        self.origin =  (self.x_of_line, self.y_of_line)
        self.image_width = self.image_generator.get_image_width()
        self.center_x_of_line = int(self.x_of_line + self.image_width / 2)
        self.x_for_all_inview_objects_for_all_camera_time = self.image_generator.get_x_for_all_inview_objects_for_all_camera_time()
        super().__init__(**kargs)

    def set_object_stats_processor(self, object_stats_processor):
        self.object_stats_processor = object_stats_processor
        return self

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
        self.moving_rendered_elements.append(self.get_dot(coords, obj, timestamp))
        self.moving_rendered_elements.append(self.get_dot_label(coords, obj, timestamp, anchor=self.get_anchor(obj, timestamp)))

    def get_anchor(self, obj, timestamp):
        if self.get_eliminated(obj, timestamp):
            return 'ne'
        else:
            return 'se'

    def get_eliminated(self, obj, timestamp):
        if self.object_stats_processor == None:
            return False
        else:
            return obj in self.object_stats_processor.get_all_eliminated_before_timestamp(timestamp)

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


class BasePositionCalibratorRenderer(ElementRenderer):

    def __init__(self, base_position_calibrator, **kargs):
        '''
        :param BasePositionCalibrator base_position_calibrator:
        '''
        self.base_position_calibrator = base_position_calibrator
        self.cc_color = 'orange'
        self.dot_color = 'blue'
        self.early_late_points = None
        super().__init__(**kargs)

    def render_stationary_elements(self):
        self.delete_stationary_rendered_elements()
        for isect in self.base_position_calibrator.get_all_error_circle_intersections():
            self.stationary_rendered_elements.append(self.tk_renderer.create_line(isect.coords,
                                                                                  fill=self.cc_color,
                                                                                  smooth=True,
                                                                                  ))

    def render_moving_elements(self, timestamp):
        self.delete_moving_rendered_elements()
        if timestamp in self._get_early_late_points():
            self.stationary_rendered_elements.append(self.tk_renderer.create_dot(self.early_late_points[timestamp],
                                                                             fill=self.dot_color,
                                                                             outline=self.dot_color,
                                                                             size=3))

    def _get_object_motion_analyzer(self):
        '''
        :rtype ObjectMotionAnalyzer
        '''
        return self.base_position_calibrator.get_object_motion_analyzer()

    def _get_tag_position_analyzer(self):
        '''
        :rtype TagPositionAnalzyer
        '''
        return self._get_object_motion_analyzer().get_tag_position_analyzer()

    def _get_frames(self):
        return self._get_object_motion_analyzer().get_complete_frames()

    def _get_early_late_points(self):
        if self.early_late_points == None:
            self.early_late_points = {}
            for frame in self._get_frames():
                etime = self._get_tag_position_analyzer().get_early_min_max_timestamp(frame)
                ltime = self._get_tag_position_analyzer().get_late_min_max_timestamp(frame)
                epos  = self._get_tag_position_analyzer().get_early_position(frame)
                lpos  = self._get_tag_position_analyzer().get_late_position(frame)
                self.early_late_points[etime] = epos
                self.early_late_points[ltime] = lpos

        return self.early_late_points


class PhotoRenderer(ElementRenderer):

    def __init__(self, image):
        self.image = image
        super().__init__()

    def render_stationary_elements(self):
        self.stationary_rendered_elements.append(self.tk_renderer.create_photo((0,0), self.image))
