import math
import geometry_utils as GU
from tag_position_analyzer import TagPositionAnalyzer
from image_analyzer import ImageAnalyzer 
from shapely.geometry import Point

class ObjectMotionAnalyzer:

    def __init__(self, camera, tag, tag_gps_angle_threshold=math.radians(3)):
        self.camera = camera
        self.tag = tag
        self.tag_position_analyzer = TagPositionAnalyzer(tag, camera)
        self.tag_gps_angle_threshold = tag_gps_angle_threshold
        self.frames = None
        self.image_analyzer = None
    
    def get_tag_gps_angle_threshold(self):
        return self.tag_gps_angle_threshold

    def set_tag_gps_angle_threshold(self, theta_rad):
        self.tag_gps_angle_threshold = theta_rad
        return self
    
    def get_tag_position_analyzer(self):
        return self.tag_position_analyzer

    def re_analyze(self):
        self.frames = None
        self.image_analyzer = None
        return self

    def get_frames(self):
        if self.frames == None:
            self._analyze_frames()
        
        return self.frames

    def _analyze_frames(self):
        self.frames = self.tag_position_analyzer.get_frames_where_range_exceeds_threshold(self.tag_gps_angle_threshold)
        for frame in self.frames:
            self._analyze_frame(frame)
        
        return self

    def _get_frame_rotation_same_as_tag(self, frame):
        if not 'rotation_same_as_tag' in frame:
            frame['rotation_same_as_tag'] = {}
        return frame['rotation_same_as_tag']
    
    def _get_frame_in_view_object_angles(self, frame):
        return frame['in_view_objects_angles'] if not self.is_terminal_frame(frame) else None

    def _get_image_analyzer(self):
        if self.image_analyzer == None:
            self.image_analyzer = ImageAnalyzer(self.camera)
            self.image_analyzer.set_images(self.camera.get_image_generator().get_x_for_all_inview_objects_for_all_camera_time())
        return self.image_analyzer
    
    def _analyze_frame(self, frame):
        if not self.tag_position_analyzer.is_terminal_frame(frame): 
            self._add_objects_angles_to_frame(frame)
            self._mark_objects_with_rotation_same_as_tag_in_frame(frame)
            self._add_circumcircles_for_objects_in_frame(frame)
        
    def _mark_objects_with_rotation_same_as_tag_in_frame(self, frame):
        for obj in self._get_frame_in_view_object_angles(frame):
            self._get_frame_rotation_same_as_tag(frame)[obj] = (self.tag_position_analyzer.get_angle_between_positions(frame) > 0) == \
                                                               (self._get_frame_in_view_object_angles(frame)[obj] > 0)

    def _add_circumcircles_for_objects_in_frame(self, frame):
        for obj in self.get_in_view_objects(frame):
            p1 = self.tag_position_analyzer.get_early_position(frame)
            p2 = self.tag_position_analyzer.get_late_position(frame)
            theta_rad = self._get_frame_in_view_object_angles(frame)[obj]
            error_circle_center = self.camera.get_gps_position()
            error_circle_radius = self.camera.get_gps_max_error()
            self.get_circumcircles(frame)[obj] = Circumcircles(p1, p2, theta_rad, error_circle_center, error_circle_radius)

        return self

    def get_in_view_objects(self, frame):
        return self._get_frame_in_view_object_angles(frame).keys() if not self.is_terminal_frame(frame) else []
    
    def get_rotation_same_as_tag(self, frame, obj):
        rot_s = self._get_frame_rotation_same_as_tag(frame)
        return rot_s[obj] if obj in rot_s else None
    
    def get_circumcircles(self, frame):
        if 'circumcircles' not in frame:
            frame['circumcircles'] = {}
        return frame['circumcircles']
    
    def get_circumcircles_for_object_in_frame(self, frame, obj):
        return self.get_circumcircles(frame)[obj] if obj in self.get_circumcircles(frame) else None 
        
    def is_terminal_frame(self, frame):
        return self.tag_position_analyzer.is_terminal_frame(frame)

    def get_tag(self, frame):
        for obj in self.get_in_view_objects(frame):
            if obj != None and obj.get_is_tag():
                return obj
        
        return None

    def _add_objects_angles_to_frame(self, frame):
        ts1 = self.tag_position_analyzer.get_early_min_max_timestamp(frame)
        ts2 = self.tag_position_analyzer.get_late_min_max_timestamp(frame)
        frame['in_view_objects_angles'] = self._get_image_analyzer().get_subtended_angles_for_all_objects(ts1, ts2)
        return self
    

class Circumcircles:

    def __init__(self, early_postion, late_position, theta_rad, error_circle_center, error_circle_radius):
        self.high_def_res = 10000
        self.low_def_res = 100

        self.error_circle_center = error_circle_center
        self.error_circle_radius = error_circle_radius
        self.theta_rad = theta_rad
        self.p1 = early_postion
        self.p2 = late_position

        self.circumcenters = None
        self.circumradius = None

        self.error_circle_exterior = None
        self.error_circle_disk = None

        self.c1_high_def = None
        self.c1_low_def = None

        self.c2_high_def = None
        self.c2_low_def = None
    
        self.c1_intersects_error_circle = None
        self.c2_intersects_error_circle = None

        self.c1_error_circle_intersection = None
        self.c2_error_circle_intersection = None

    def get_circumcenters(self):
        if self.circumcenters == None:
            self.circumcenters = GU.circumcenters(self.p1, self.p2, self.theta_rad)
        return self.circumcenters

    def get_circumradius(self):
        if self.circumradius == None:
            self.circumradius = GU.circumradius(self.p1, self.p2, self.theta_rad)
        return self.circumradius

    def get_error_circle_exterior(self):
        if self.error_circle_exterior == None:
            self.error_circle_exterior = Point(self.error_circle_center).buffer(self.error_circle_radius, resolution=self.low_def_res).exterior #pylint: disable=no-member
        return self.error_circle_exterior

    def get_error_circle_disk(self):
        if self.error_circle_disk == None:
            self.error_circle_disk = Point(self.error_circle_center).buffer(self.error_circle_radius, resolution=self.high_def_res)
        return self.error_circle_disk

    def get_c1_low_def(self):
        if self.c1_low_def == None:
            self.c1_low_def = Point(self.get_circumcenters()[0]).buffer(self.get_circumradius(), self.low_def_res).exterior #pylint: disable=no-member
        return self.c1_low_def

    def get_c2_low_def(self):
        if self.c2_low_def == None:
            self.c2_low_def = Point(self.get_circumcenters()[1]).buffer(self.get_circumradius(), self.low_def_res).exterior #pylint: disable=no-member
        return self.c1_low_def

    def get_c1_high_def(self):
        if self.c1_high_def == None:
            self.c1_high_def = Point(self.get_circumcenters()[0]).buffer(self.get_circumradius(), self.high_def_res).exterior #pylint: disable=no-member
        return self.c1_high_def

    def get_c2_high_def(self):
        if self.c2_high_def == None:
            self.c2_high_def = Point(self.get_circumcenters()[1]).buffer(self.get_circumradius(), self.high_def_res).exterior #pylint: disable=no-member
        return self.c1_high_def

    def get_c1_intersects_error_circle(self):
        if self.c1_intersects_error_circle == None:
            self.c1_intersects_error_circle = self.get_c1_low_def().intersects(self.get_error_circle_exterior())
        return self.c1_intersects_error_circle
    
    def get_c2_intersects_error_circle(self):
        if self.c2_intersects_error_circle == None:
            self.c2_intersects_error_circle = self.get_c2_low_def().intersects(self.get_error_circle_exterior())
        return self.c2_intersects_error_circle
    
    def get_intersects_error_circle(self):
        return self.get_c1_intersects_error_circle() or self.get_c2_intersects_error_circle()

    def get_c1_error_circle_intersection(self):
        if self.c1_error_circle_intersection == None and self.get_c1_intersects_error_circle():
            self.c1_error_circle_intersection = self.get_c1_high_def().intersection(self.get_error_circle_disk())
        return self.c1_error_circle_intersection

    def get_c2_error_circle_intersection(self):
        if self.c2_error_circle_intersection == None and self.get_c2_intersects_error_circle():
            self.c2_error_circle_intersection = self.get_c2_high_def().intersection(self.get_error_circle_disk())
        return self.c2_error_circle_intersection

    def get_error_circle_intersection(self):
        if self.get_c1_error_circle_intersection() != None:
            return self.get_c1_error_circle_intersection()
        return self.get_c2_error_circle_intersection()