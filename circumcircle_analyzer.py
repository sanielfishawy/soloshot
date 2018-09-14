import math
import geometry_utils as GU
from tag_position_analyzer import TagPositionAnalyzer
from image_analyzer import ImageAnalyzer 
from shapely.geometry import Point

class CircumcircleAnalyzer:

    def __init__(self, camera, tag):
        self.camera = camera
        self.tag = tag
        self.tag_position_analyzer = TagPositionAnalyzer(tag, camera)
        self.tag_gps_angle_threshold = math.radians(3)
        self.frames = None
        self.error_circle = None
    
    def get_analyzed_frames(self):
        for frame in self._get_frames():
            self._analyze_frame(frame)
        return self._get_frames()

    def _get_frames(self):
        if self.frames == None:
            self.frames = self.tag_position_analyzer.get_frames_where_range_exceeds_threshold(self.tag_gps_angle_threshold)
        return self.frames

    def _get_frame_rotation_same_as_tag(self, frame):
        if not 'rotation_same_as_tag' in frame:
            frame['rotation_same_as_tag'] = {}
        return frame['rotation_same_as_tag']
    
    def _get_frame_circumcircles(self, frame):
        if not 'circumcircles' in frame:
            frame['circumcircles'] = {}
        return frame['circumcircles']
    
    def _get_frame_in_view_object_angles(self, frame):
        return frame['in_view_objects_angles']

    def _get_image_analyzer(self):
        self.image_analyzer = ImageAnalyzer(self.camera)
        self.image_analyzer.set_images(self.camera.get_image_generator().get_x_for_all_inview_objects_for_all_camera_time())
        return self.image_analyzer
    
    def _get_error_circle(self):
        if self.error_circle == None:
            self.error_circle = Point(self.camera.get_gps_position()).buffer(self.camera.get_gps_max_error(), resolution=10000)
        return self.error_circle

    def _analyze_frame(self, frame):
        self._add_objects_angles_to_frame(frame)
        self._mark_objects_with_rotation_same_as_tag_in_frame(frame)
        self._add_circumcircles_for_objects_in_frame(frame)
        
    def _mark_objects_with_rotation_same_as_tag_in_frame(self, frame):
        for obj in self._get_frame_in_view_object_angles(frame):
            self._get_frame_rotation_same_as_tag(frame)[obj] = self.tag_position_analyzer.get_angle_between_positions(frame) > 0 ==\
                                                               self._get_frame_in_view_object_angles(frame)[obj] > 0

    def _add_circumcircles_for_objects_in_frame(self, frame):
        p1 = self.tag_position_analyzer.get_early_position(frame)
        p2 = self.tag_position_analyzer.get_late_position(frame)

        for obj in self._get_frame_in_view_object_angles(frame):
            if not self._get_frame_rotation_same_as_tag(frame)[obj]:
                self._get_frame_circumcircles(frame)[obj] = None
                next

            theta_rad = self._get_frame_in_view_object_angles(frame)[obj]

            self._get_frame_circumcircles(frame)[obj] = {}
            cc = self._get_frame_circumcircles(frame)[obj]
            cc['circumcenters'] = GU.circumcenters(p1, p2, theta_rad)
            r = GU.circumradius(p1, p2, theta_rad)
            cc['circumradius'] = r
            cc['c1'] = Point(p1).buffer(r, resolution=10000).exterior #pylint: disable=no-member
            cc['c2'] = Point(p2).buffer(r, resolution=10000).exterior #pylint: disable=no-member
        
            cc['intersects_error_circle'] = False
            cc['error_circle_intersection'] = None
            if cc['c1'].intersects(self._get_error_circle()):
                cc['intersects_error_circle'] = True
                cc['error_circle_intersection'] = cc['c1'].intersection(self._get_error_circle())
            elif cc['c2'].intersects(self._get_error_circle()):
                cc['intersects_error_circle'] = True
                cc['error_circle_intersection'] = cc['c2'].intersection(self._get_error_circle())

    def _add_objects_angles_to_frame(self, frame):
        ts1 = self.tag_position_analyzer.get_early_min_max_timestamp(frame)
        ts2 = self.tag_position_analyzer.get_late_min_max_timestamp(frame)
        frame['in_view_objects_angles'] = self._get_image_analyzer().get_subtended_angles_for_all_objects(ts1, ts2)