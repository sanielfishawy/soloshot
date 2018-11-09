import math
import geometry_utils as GUtils

class TagPositionAnalyzer:

    FRAME = 'frame'
    TIMESTAMP_OF_MIN_ANGLE = 'timestamp_of_min_angle'
    TIMESTAMP_OF_MAX_ANGLE = 'timestamp_of_max_angle'
    DISTANCE_BETWEEN_POSITIONS = 'distance_between_positions'
    ANGLE_BETWEEN_POSITIONS = 'angle_between_positions'


    def __init__(self, tag, camera):
        self.tag = tag
        self.camera = camera

        self._frames = None

    def _angle_to_tag(self, timestamp):
        tag_position = self.tag.get_position_at_timestamp(timestamp)
        return GUtils.angel_of_vector_between_points_360_rad(
            self.camera.get_gps_position(),
            tag_position
        )

    def _q4_adjusted_angle_to_tag(self, timestamp):
        r = self._angle_to_tag(timestamp)
        if self._quadrant_to_tag(timestamp) == 4:
            r = r - 2 * math.pi
        return r

    def _quadrant_to_tag(self, timestamp):
        tag_position = self.tag.get_position_at_timestamp(timestamp)
        return GUtils.quadrant_of_vector(self.camera.get_gps_position(), tag_position)

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
        self._frames = []
        frame_start = 0
        frame_end = None
        for _ in range(self.tag.get_num_timestamps()):
            frame_end = self._first_time_after_timestamp_where_range_of_angles_exceeds_threshold(frame_start, threshold_rad)
            frame = {}
            frame[self.__class__.FRAME] = (frame_start, frame_end)
            if frame_end is not None:
                min_ts = self._timestamp_of_min_angle_in_frame(frame_start, frame_end)
                max_ts = self._timestamp_of_max_angle_in_frame(frame_start, frame_end)
                frame[self.__class__.TIMESTAMP_OF_MIN_ANGLE] = min_ts
                frame[self.__class__.TIMESTAMP_OF_MAX_ANGLE] = max_ts
                frame[self.__class__.DISTANCE_BETWEEN_POSITIONS] = self._distance_between_positions(min_ts, max_ts)
                frame[self.__class__.ANGLE_BETWEEN_POSITIONS] = self._angle_between_timestamps(min_ts, max_ts)
            self._frames.append(frame)
            frame_start = frame_end

            if frame_end is None:
                break

        return self._frames

    def get_complete_frames_where_range_exceeds_threshold(self, threshold_rad):
        return [
            frame for frame in self.get_frames_where_range_exceeds_threshold(threshold_rad)
            if self.is_not_terminal_frame(frame)
        ]

    def get_early_position(self, frame):
        if self.is_terminal_frame(frame):
            return None

        return self.tag.get_position_at_timestamp(self.get_early_min_max_timestamp(frame))

    def get_late_position(self, frame):
        if self.is_terminal_frame(frame):
            return None

        return self.tag.get_position_at_timestamp(self.get_late_min_max_timestamp(frame))

    def get_early_min_max_timestamp(self, frame):
        if frame[self.__class__.TIMESTAMP_OF_MIN_ANGLE] < frame[self.__class__.TIMESTAMP_OF_MAX_ANGLE]:
            return frame[self.__class__.TIMESTAMP_OF_MIN_ANGLE]
        else:
            return frame[self.__class__.TIMESTAMP_OF_MAX_ANGLE]

    def get_late_min_max_timestamp(self, frame):
        if frame[self.__class__.TIMESTAMP_OF_MIN_ANGLE] > frame[self.__class__.TIMESTAMP_OF_MAX_ANGLE]:
            return frame[self.__class__.TIMESTAMP_OF_MIN_ANGLE]
        else:
            return frame[self.__class__.TIMESTAMP_OF_MAX_ANGLE]

    def get_frame_start_timestamp(self, frame):
        return self.get_frame_bounds(frame)[0]

    def get_frame_end_timestamp(self, frame):
        return self.get_frame_bounds(frame)[1]

    def get_frame_bounds(self, frame):
        return frame[self.__class__.FRAME]

    def get_distance_between_positions(self, frame):
        return frame[self.__class__.DISTANCE_BETWEEN_POSITIONS]

    def get_timestamp_of_max_angle(self, frame):
        return frame[self.__class__.TIMESTAMP_OF_MAX_ANGLE]

    def get_timestamp_of_min_angle(self, frame):
        return frame[self.__class__.TIMESTAMP_OF_MIN_ANGLE]

    def get_angle_between_positions(self, frame):
        return frame[self.__class__.ANGLE_BETWEEN_POSITIONS]

    def get_last_complete_frame(self):
        f = self._frames[-1]
        if self.is_terminal_frame(f) and len(self._frames) >= 2:
            f = self._frames[-2]
        return f

    def is_not_terminal_frame(self, frame):
        return not self.is_terminal_frame(frame)

    def is_terminal_frame(self, frame):
        return self.get_frame_end_timestamp(frame) is None

    def _distance_between_positions(self, timestamp1, timestamp2):
        return GUtils.distance_between_points(self.tag.get_position_at_timestamp(timestamp1),
                                              self.tag.get_position_at_timestamp(timestamp2))

    # Lower timestamp is a assumed to happen first
    # Clockwise movement in time looking down gives negative angle
    # Counterclockwise movement in time looking down gives positive angle
    def _angle_between_timestamps(self, timestamp1, timestamp2):
        t1, t2 = (timestamp1, timestamp2) if timestamp1 < timestamp2 else (timestamp2, timestamp1)
        p1 = self.tag.get_position_at_timestamp(t1)
        p2 = self.tag.get_position_at_timestamp(t2)
        return GUtils.signed_subtended_angle_from_p1_to_p2_rad(self.camera.get_gps_position(), p1, p2)


    def _crosses_q1_4_boundary(self, quadrants):
        return 1 in quadrants.keys() and 4 in quadrants.keys()

