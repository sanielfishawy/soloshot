from object_motion_analyzer import ObjectMotionAnalyzer, Circumcircles
from tag_position_analyzer import TagPositionAnalyzer

class BaseCalibrator:

    def __init__(self):
        pass


class ObjectsStatsProcessor:
    moved_opposite_to_tag_n = 'moved_opposite_to_tag_n'
    moved_opposite_to_tag_t = 'moved_opposite_to_tag_t'
    didnt_intersect_error_circle_n = 'didnt_intersect_n'
    didnt_intersect_error_circle_t = 'didnt_intersect_t'
    elimination = 'elimination_time'

    def __init__(self, object_motion_analyzer):
        """
        :type object_motion_analyzer: ObjectMotionAnalyzer
        :type tag_position_analyzer: TagPositionAnalyzer
        """
        self.object_motion_analyzer = object_motion_analyzer
        self.tag_position_analyzer = self.object_motion_analyzer.get_tag_position_analyzer()
        self.processed_objects = {}

    def get_processed_objects(self):
        if self.processed_objects == {}:
            self._process_objects()
        return self.processed_objects
    
    def _process_objects(self):
        for frame in self.object_motion_analyzer.get_frames():
            for obj in self.object_motion_analyzer.get_in_view_objects(frame):
                self._process_object(frame, obj)

    def _process_object(self, frame, obj):
        self._set_moved_opposite_to_tag(frame, obj)
        self._set_didnt_intersect_error_circle(frame, obj)
    
    def _set_moved_opposite_to_tag(self, frame, obj):
        self.get_moved_opposite_to_tag_n(obj) #init
        self.get_moved_opposite_to_tag_t(obj) #init
        if not self.object_motion_analyzer.get_rotation_same_as_tag(frame, obj):
            self._get_hash_for_obj(obj)[self.moved_opposite_to_tag_n] = self.get_moved_opposite_to_tag_n(obj) + 1
            if self.get_moved_opposite_to_tag_t(obj) == None:
                self._get_hash_for_obj(obj)[self.moved_opposite_to_tag_t] = self.tag_position_analyzer.get_early_position(frame)
    
    def _set_didnt_intersect_error_circle(self, frame, obj):
        """
        :type cc: Circumcircles
        """
        self.get_didnt_intersect_error_circle_n(obj) #init
        self.get_didnt_intersect_error_circle_t(obj) #init
        cc = self.object_motion_analyzer.get_circumcircles_for_object_in_frame(frame, obj)
        if cc != None and not cc.get_intersects_error_circle():
            self._get_hash_for_obj(obj)[self.didnt_intersect_error_circle_n] = self.get_didnt_intersect_error_circle_n(obj) + 1
            if self.get_didnt_intersect_error_circle_t(obj) == None:
                self._get_hash_for_obj(obj)[self.didnt_intersect_error_circle_t] = self.tag_position_analyzer.get_early_position(frame)

    def _get_hash_for_obj(self, obj):
        if obj not in self.processed_objects:
            self.processed_objects[obj]= {}
        return self.processed_objects[obj]

    def get_moved_opposite_to_tag_n(self, obj):
        if self.moved_opposite_to_tag_n not in self._get_hash_for_obj(obj):
            self._get_hash_for_obj(obj)[self.moved_opposite_to_tag_n] = 0
        return self._get_hash_for_obj(obj)[self.moved_opposite_to_tag_n] 
    
    def get_moved_opposite_to_tag_t(self, obj):
        if self.moved_opposite_to_tag_t not in self._get_hash_for_obj(obj):
            self._get_hash_for_obj(obj)[self.moved_opposite_to_tag_t] = None
        return self._get_hash_for_obj(obj)[self.moved_opposite_to_tag_t] 
    
    def get_did_move_opposite_to_tag(self, obj):
        return self.get_moved_opposite_to_tag_t(obj) != None
    
    def get_didnt_move_opposite_to_tag(self, obj):
        return not self.get_did_move_opposite_to_tag(obj)

    def get_didnt_intersect_error_circle_n(self, obj):
        if self.didnt_intersect_error_circle_n not in self._get_hash_for_obj(obj):
            self._get_hash_for_obj(obj)[self.didnt_intersect_error_circle_n] = 0
        return self._get_hash_for_obj(obj)[self.didnt_intersect_error_circle_n]
    
    def get_didnt_intersect_error_circle_t(self, obj):
        if self.didnt_intersect_error_circle_t not in self._get_hash_for_obj(obj):
            self._get_hash_for_obj(obj)[self.didnt_intersect_error_circle_t] = None
        return self._get_hash_for_obj(obj)[self.didnt_intersect_error_circle_t]
    
    def get_didnt_intersect_error_circle(self, obj):
        return self.didnt_intersect_error_circle_t != None
    
    def get_objects_that_always_moved_same_direction_as_tag(self):
        objs = [obj for obj in self.get_processed_objects()]
        return list(filter(self.get_didnt_move_opposite_to_tag, [obj for obj in self.get_processed_objects()]))

    def get_top_ranked_object(self):
        r = self.get_ranked_objects()
        return r[0] if len(r) > 0 else None
        
    def get_ranked_objects(self):
        l = self.get_objects_that_always_moved_same_direction_as_tag()
        l.sort(key=self.get_didnt_intersect_error_circle_n)
        return l
