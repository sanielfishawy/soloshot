import math
import geometry_utils as GUtils

class TagPositionAnalyzer:

    def __init__(self, tag, camera):
        self.tag = tag
        self.camera = camera

    def _angle_to_tag(self, timestamp):
        tag_position = self.tag.get_position_at_timestamp(timestamp)
        return GUtils.angel_of_vector_between_points_360_rad(self.camera.get_gps_position(), tag_position)
    
    def _q4_adjusted_angle_to_tag(self, timestamp):
        r = self._angle_to_tag(timestamp)
        if self._quadrant_to_tag(timestamp) == 4:
            r = r - 2 * math.pi
        return r
    
    def _quadrant_to_tag(self, timestamp):
        tag_position = self.tag.get_position_at_timestamp(timestamp)
        return GUtils.quadrant_of_vector(self.camera.gps_position, tag_position)
    
    def _range_of_angles_between_timestamps(self, timestamp1, timestamp2):
        a = self._list_of_angles_between_timestamps(timestamp1, timestamp2)
        return max(a) - min(a)
    
    def _timestamp_of_min_angle_in_frame(self, timestamp1, timestamp2):
        a_s = self._list_of_angles_between_timestamps(timestamp1, timestamp2)
        mn = min(a_s)
        for i, a in enumerate(a_s):
            if a == mn:
                return i + timestamp1
        return None

    def _timestamp_of_max_angle_in_frame(self, timestamp1, timestamp2):
        a_s = self._list_of_angles_between_timestamps(timestamp1, timestamp2)
        mx = max(a_s)
        for i, a in enumerate(a_s):
            if a == mx:
                return i + timestamp1
        return None

    def _list_of_angles_between_timestamps(self, timestamp1, timestamp2):
        angles = []
        angles_q4_adjusted = []
        quadrants = {}
        for timestamp in range(timestamp1, timestamp2+1):
            quadrant = self._quadrant_to_tag(timestamp)
            quadrants[quadrant] = True
            angles.append(self._angle_to_tag(timestamp)) 
            angles_q4_adjusted.append(self._q4_adjusted_angle_to_tag(timestamp))
        
        return angles_q4_adjusted if self._crosses_q1_4_boundary(quadrants) else angles
        
    def _first_time_after_timestamp_where_range_of_angles_exceeds_threshold(self, timestamp, threshold):
        r = None
        for ts in range(timestamp, self.tag.get_num_timestamps()):
            if self._range_of_angles_between_timestamps(timestamp, ts) > threshold:
                r = ts
                break

        return r
    
    def get_frames_where_range_exceeds_threshold(self, threshold_rad):
        r = []
        frame_start = 0
        frame_end = None
        for _ in range(self.tag.get_num_timestamps()):
            frame_end = self._first_time_after_timestamp_where_range_of_angles_exceeds_threshold(frame_start, threshold_rad)
            frame = {}
            frame['frame'] = (frame_start, frame_end)
            if frame_end != None:
                frame['timestamp_of_min_angle'] = self._timestamp_of_min_angle_in_frame(frame_start, frame_end)
                frame['timestamp_of_max_angle'] = self._timestamp_of_max_angle_in_frame(frame_start, frame_end)
            r.append(frame)
            frame_start = frame_end

            if frame_end == None:
                break
        
        return r
    
    def _crosses_q1_4_boundary(self, quadrants):
        return 1 in quadrants.keys() and 4 in quadrants.keys()

