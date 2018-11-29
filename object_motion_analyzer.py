import math
from tag_position_analyzer import TagPositionAnalyzer
from image_analyzer import ImageAnalyzer
from circumcircles import Circumcircles

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
        if self.frames is None:
            self._analyze_frames()

        return self.frames

    def get_complete_frames(self):
        return list(filter(self.is_not_terminal_frame, self.get_frames()))

    def get_first_complete_frame(self):
        f = self.get_complete_frames()
        if len(f) == 0:
            return None
        return f[0]

    def get_first_frame_with_object(self, obj):
        for f in self.get_complete_frames():
            if self.get_frame_includes_object(f, obj):
                return f
        return None

    def get_frame_includes_object(self, frame, obj):
        return obj in self.get_in_view_objects(frame)

    def _analyze_frames(self):
        self.frames = self.tag_position_analyzer.get_frames_where_range_exceeds_threshold(
            threshold_rad=self.tag_gps_angle_threshold,
            min_distance_to_camera=0,
        )
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
        if self.image_analyzer is None:
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

    def get_circumcircles_for_object_for_all_frames(self, obj):
        return [self.get_circumcircles_for_object_in_frame(frame, obj) for frame in self.get_complete_frames()]

    def is_not_terminal_frame(self, frame):
        return self.tag_position_analyzer.is_not_terminal_frame(frame)

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
        frame['in_view_objects_angle_relative_to_center_early'] = self._get_image_analyzer().get_angles_relative_to_center_for_all_objects(ts1)
        frame['in_view_objects_angle_relative_to_center_late']  = self._get_image_analyzer().get_angles_relative_to_center_for_all_objects(ts2)
        return self

    def get_early_angle_relative_to_center(self, frame):
        if 'in_view_objects_angle_relative_to_center_early' not in frame:
            frame['in_view_objects_angle_relative_to_center_early'] = {}
        return frame['in_view_objects_angle_relative_to_center_early']

    def get_early_angle_relative_to_center_for_object_in_frame(self, obj, frame):
        return self.get_early_angle_relative_to_center(frame)[obj] if obj in self.get_early_angle_relative_to_center(frame) else None
