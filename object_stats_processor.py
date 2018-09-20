from object_motion_analyzer import ObjectMotionAnalyzer, Circumcircles
from tag_position_analyzer import TagPositionAnalyzer

class ObjectsStatsProcessor:
    moved_opposite_to_tag_n = 'moved_opposite_to_tag_n'
    moved_opposite_to_tag_t = 'moved_opposite_to_tag_t'
    didnt_intersect_error_circle_n = 'didnt_intersect_n'
    didnt_intersect_error_circle_t = 'didnt_intersect_t'
    eliminated = 'eliminated'
    elimination_t = 'elimination_t'

    def __init__(self, object_motion_analyzer):
        """
        :type object_motion_analyzer: ObjectMotionAnalyzer
        """
        self._object_motion_analyzer = object_motion_analyzer
        self._processed_objects = {}

    def get_tag_position_analyzer(self):
        """
        :rtype TagPositionAnalyzer
        """
        return self._object_motion_analyzer.get_tag_position_analyzer()

    def get_processed_objects(self):
        if self._processed_objects == {}:
            self._process_objects()
        return self._processed_objects
    
    def get_object_motion_analyzer(self):
        return self._object_motion_analyzer

    def _process_objects(self):
        self._process_moved_opposite()
        self._process_intersection()
        self._set_eliminated_for_all_moved_same_as_tag_which_are_not_top_ranked_object()

    def _process_moved_opposite(self):
        for frame in self._object_motion_analyzer.get_frames():
            for obj in self._object_motion_analyzer.get_in_view_objects(frame):
                self._set_moved_opposite_to_tag(frame, obj)

    def _process_intersection(self):
        for frame in self._object_motion_analyzer.get_frames():
            for obj in self._object_motion_analyzer.get_in_view_objects(frame):
                self.get_didnt_intersect_error_circle_n(obj) #init
                self.get_didnt_intersect_error_circle_t(obj) #init
                if not self.get_eliminated(obj): # only do expenensive intersection analysis for objects that never moved opposite
                    self._set_didnt_intersect_error_circle(frame, obj)

    def _process_object(self, frame, obj):
        self._set_moved_opposite_to_tag(frame, obj)
        self._set_didnt_intersect_error_circle(frame, obj)
    
    def _set_moved_opposite_to_tag(self, frame, obj):
        self.get_moved_opposite_to_tag_n(obj) #init
        self.get_moved_opposite_to_tag_t(obj) #init
        self.get_eliminated(obj) #init
        self.get_elimination_t(obj) #init
        if not self._object_motion_analyzer.get_rotation_same_as_tag(frame, obj):
            self._get_hash_for_obj(obj)[self.moved_opposite_to_tag_n] = self.get_moved_opposite_to_tag_n(obj) + 1
            self._get_hash_for_obj(obj)[self.eliminated] = True
            if self.get_moved_opposite_to_tag_t(obj) == None:
                self._get_hash_for_obj(obj)[self.elimination_t] = self.get_tag_position_analyzer().get_early_min_max_timestamp(frame)
                self._get_hash_for_obj(obj)[self.moved_opposite_to_tag_t] = self.get_tag_position_analyzer().get_early_min_max_timestamp(frame)
    
    def _set_didnt_intersect_error_circle(self, frame, obj):
        """
        :type cc: Circumcircles
        """
        cc = self._object_motion_analyzer.get_circumcircles_for_object_in_frame(frame, obj)

        if self.get_didnt_intersect_error_circle_n(obj) == None:
            self._get_hash_for_obj(obj)[self.didnt_intersect_error_circle_n] = 0

        if cc != None and not cc.get_intersects_error_circle():
            self._get_hash_for_obj(obj)[self.didnt_intersect_error_circle_n] = self.get_didnt_intersect_error_circle_n(obj) + 1

            if self.get_didnt_intersect_error_circle_t(obj) == None:
                self._get_hash_for_obj(obj)[self.didnt_intersect_error_circle_t] = self.get_tag_position_analyzer().get_early_min_max_timestamp(frame)

    def _set_eliminated_for_all_moved_same_as_tag_which_are_not_top_ranked_object(self):
        for obj in self.get_ranked_objects():
            if obj not in self.get_top_ranked_objects():
                self._get_hash_for_obj(obj)[self.eliminated] = True
                self._get_hash_for_obj(obj)[self.elimination_t] = self.get_tag_position_analyzer().get_early_min_max_timestamp(self.get_tag_position_analyzer().get_last_complete_frame())

    def _get_hash_for_obj(self, obj):
        if obj not in self._processed_objects:
            self._processed_objects[obj]= {}
        return self._processed_objects[obj]

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
            self._get_hash_for_obj(obj)[self.didnt_intersect_error_circle_n] = None
        return self._get_hash_for_obj(obj)[self.didnt_intersect_error_circle_n]
    
    def get_didnt_intersect_error_circle_t(self, obj):
        if self.didnt_intersect_error_circle_t not in self._get_hash_for_obj(obj):
            self._get_hash_for_obj(obj)[self.didnt_intersect_error_circle_t] = None
        return self._get_hash_for_obj(obj)[self.didnt_intersect_error_circle_t]
    
    def get_didnt_intersect_error_circle(self, obj):
        return self.didnt_intersect_error_circle_t != None
    
    def get_elimination_t(self, obj):
        if self.elimination_t not in self._get_hash_for_obj(obj):
            self._get_hash_for_obj(obj)[self.elimination_t] = None
        return self._get_hash_for_obj(obj)[self.elimination_t]

    def get_eliminated(self, obj):
        if self.eliminated not in self._get_hash_for_obj(obj):
            self._get_hash_for_obj(obj)[self.eliminated] = False
        return self._get_hash_for_obj(obj)[self.eliminated]
    
    def get_all_eliminated(self):
        return list(filter(self.get_eliminated, [obj for obj in self.get_processed_objects()]))
    
    def get_all_that_always_moved_same_direction_as_tag(self):
        return list(filter(self.get_didnt_move_opposite_to_tag, [obj for obj in self.get_processed_objects()]))

    def get_all_moved_oposite(self):
        return list(filter(self.get_did_move_opposite_to_tag, [obj for obj in self.get_processed_objects()]))

    def get_all_no_intersect(self):
        return list(filter(self.get_didnt_intersect_error_circle, [obj for obj in self.get_processed_objects()]))

    def get_top_ranked_object(self):
        r = self.get_ranked_objects()
        return r[0] if len(r) > 0 else None
    
    def get_top_ranked_objects(self):
        return list(filter(self.get_had_same_didnt_intersect_n_as_top_ranked, self.get_ranked_objects()))

    def get_had_same_didnt_intersect_n_as_top_ranked(self, obj):
        return self.get_didnt_intersect_error_circle_n(self.get_top_ranked_object()) == self.get_didnt_intersect_error_circle_n(obj)

    def get_ranked_objects(self):
        l = self.get_all_that_always_moved_same_direction_as_tag()
        l.sort(key=self.get_didnt_intersect_error_circle_n)
        return l

    def get_all_eliminated_before_timestamp(self, timestamp):
        e_tuples = list(filter(self._eliminated_time_is_before_timestamp, [(obj, timestamp) for obj in self.get_all_eliminated()] ))
        return [t[0] for t in e_tuples]
    
    def _eliminated_time_is_before_timestamp(self, obj_timestamp_tuple):
        obj, timestamp = obj_timestamp_tuple
        return self.get_elimination_t(obj) != None and self.get_elimination_t(obj) <= timestamp