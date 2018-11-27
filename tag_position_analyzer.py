import math
import numpy as np
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

        # lazy init
        self._tag_distances_to_camera = None
        self._tag_postions = None
        self._tag_angles = None
        self._tag_q4_adjusted_angles = None
        self._tag_quadrants = None
        self._frames = None

    def _get_tag_positions(self):
        if self._tag_postions is None:
            self._tag_postions = self.tag.get_position_history()
        return self._tag_postions

    def _get_tag_angles(self):
        if self._tag_angles is None:
            self._tag_angles = np.array(
                [
                    GUtils.angle_of_vector_between_points_360_rad(
                        self.camera.get_gps_position(),
                        tag_position,
                    )
                    for tag_position
                    in self._get_tag_positions()
                ]
            )
        return self._tag_angles

    def _get_tag_q4_adjusted_angles(self):
        if self._tag_q4_adjusted_angles is None:
            self._tag_q4_adjusted_angles = np.array(
                [
                    self._q4_adjusted_angle_to_tag(timestamp)
                    for timestamp
                    in range(self.tag.get_num_timestamps())
                ]
            )
        return self._tag_q4_adjusted_angles

    def _get_tag_quadrants(self):
        if self._tag_quadrants is None:
            self._tag_quadrants = np.array(
                [
                    GUtils.quadrant_of_vector(
                        self.camera.get_gps_position(),
                        tag_position,
                    )
                    for tag_position
                    in self._get_tag_positions()
                ]
            )
        return self._tag_quadrants

    def _get_tag_distances_to_camera(self):
        if self._tag_distances_to_camera is None:
            self._tag_distances_to_camera = np.array(
                [
                    GUtils.distance_between_points(
                        self.camera.get_gps_position(),
                        tag_position,
                    )
                    for tag_position
                    in self._get_tag_positions()
                ]
            )
        return self._tag_distances_to_camera

    def _angle_to_tag(self, timestamp):
        return self._get_tag_angles()[timestamp]

    def _q4_adjusted_angle_to_tag(self, timestamp):
        r = self._angle_to_tag(timestamp)
        if self._quadrant_to_tag(timestamp) == 4:
            r = r - 2 * math.pi
        return r

    def _quadrant_to_tag(self, timestamp):
        return self._get_tag_quadrants()[timestamp]

    def _range_of_angles_between_timestamps(
            self,
            timestamp1,
            timestamp2,
            min_distance_to_camera,
    ):
        a = self._list_of_angles_between_timestamps(
            timestamp1,
            timestamp2,
            min_distance_to_camera=min_distance_to_camera,
        )
        if a.size == 0:
            return 0

        return np.max(a) - np.min(a)

    def _timestamp_of_angle_in_frame(
            self,
            angle,
            timestamp1,
            timestamp2,
            min_distance_to_camera,
    ):
        all_angles = self._all_angles_q4_adjusted(
            timestamp1,
            timestamp2,
            min_distance_to_camera=min_distance_to_camera,
        )[timestamp1: timestamp2+1]

        for i, test_angle in enumerate(all_angles):
            if test_angle == angle and \
               self._get_tag_distances_to_camera()[i+timestamp1] >= min_distance_to_camera:
                return i + timestamp1
        return None

    def _timestamp_of_min_angle_in_frame(
            self,
            timestamp1,
            timestamp2,
            min_distance_to_camera,
    ):
        valid_angles = self._list_of_angles_between_timestamps(
            timestamp1,
            timestamp2,
            min_distance_to_camera=min_distance_to_camera,
        )
        min_angle = np.min(valid_angles)

        return self._timestamp_of_angle_in_frame(
            min_angle,
            timestamp1,
            timestamp2,
            min_distance_to_camera,
        )

    def _timestamp_of_max_angle_in_frame(
            self,
            timestamp1,
            timestamp2,
            min_distance_to_camera,
    ):
        valid_angles = self._list_of_angles_between_timestamps(
            timestamp1,
            timestamp2,
            min_distance_to_camera=min_distance_to_camera,
        )
        max_angle = np.max(valid_angles)

        return self._timestamp_of_angle_in_frame(
            max_angle,
            timestamp1,
            timestamp2,
            min_distance_to_camera,
        )

    def _all_angles_q4_adjusted(
            self,
            timestamp1,
            timestamp2,
            min_distance_to_camera,
        ):
        # Uses distance for q4 determination but does not filter final angle results
        # based on min_distance.
        if self._crosses_q1_4_boundary(timestamp1, timestamp2, min_distance_to_camera):
            return self._get_tag_q4_adjusted_angles()

        return self._get_tag_angles()

    def _list_of_angles_between_timestamps(
            self,
            timestamp1,
            timestamp2,
            min_distance_to_camera,
        ):
        angles = self._all_angles_q4_adjusted(
            timestamp1=timestamp1,
            timestamp2=timestamp2,
            min_distance_to_camera=min_distance_to_camera,
        )
        return np.take(
            angles,
            self._get_timestamps_between_timestamps_with_distance_greater_than_min(
                timestamp1,
                timestamp2,
                min_distance_to_camera,
            )
        )

    def _get_timestamps_between_timestamps_with_distance_greater_than_min(
            self,
            timestamp1,
            timestamp2,
            min_distance_to_camera,
        ):
        t_stamps = np.where(self._get_tag_distances_to_camera() >= min_distance_to_camera)[0]
        return np.take(
            t_stamps,
            np.where( (t_stamps >= timestamp1) & (t_stamps <= timestamp2))[0]
        )

    def _first_time_after_timestamp_where_range_of_angles_exceeds_threshold(
            self,
            timestamp,
            threshold,
            min_distance_to_camera,
    ):
        r = None
        for t_stamp in range(timestamp, self.tag.get_num_timestamps()):
            if self._range_of_angles_between_timestamps(
                    timestamp,
                    t_stamp,
                    min_distance_to_camera,
                ) > threshold:
                r = t_stamp
                break

        return r

    def _distance_between_positions(self, timestamp1, timestamp2):
        return GUtils.distance_between_points(self._get_tag_positions()[timestamp1],
                                              self._get_tag_positions()[timestamp2])

    # Lower timestamp is a assumed to happen first
    # Clockwise movement in time looking down gives negative angle
    # Counterclockwise movement in time looking down gives positive angle
    def _angle_between_timestamps(self, timestamp1, timestamp2):
        t1, t2 = (timestamp1, timestamp2) if timestamp1 < timestamp2 else (timestamp2, timestamp1)
        p1 = self.tag.get_position_at_timestamp(t1)
        p2 = self.tag.get_position_at_timestamp(t2)
        return GUtils.signed_subtended_angle_from_p1_to_p2_rad(self.camera.get_gps_position(), p1, p2)


    def _crosses_q1_4_boundary(
            self,
            timestamp1,
            timestamp2,
            min_distance_to_camera=0
    ):
        quadrants = np.take(
            self._get_tag_quadrants(),
            self._get_timestamps_between_timestamps_with_distance_greater_than_min(
                timestamp1,
                timestamp2,
                min_distance_to_camera,
            )
        )

        return np.any(quadrants == 1) and  np.any(quadrants == 4)

    def get_frames_where_range_exceeds_threshold(
            self,
            threshold_rad,
            min_distance_to_camera,
            limit=None,
    ):
        self._frames = []
        frame_start = 0
        frame_end = None
        for _ in range(self.tag.get_num_timestamps()):
            frame_end = self._first_time_after_timestamp_where_range_of_angles_exceeds_threshold(
                timestamp=frame_start,
                threshold=threshold_rad,
                min_distance_to_camera=min_distance_to_camera,
            )
            frame = {}
            frame[self.__class__.FRAME] = (frame_start, frame_end)
            if frame_end is not None:
                min_ts = self._timestamp_of_min_angle_in_frame(
                    timestamp1=frame_start,
                    timestamp2=frame_end,
                    min_distance_to_camera=min_distance_to_camera,
                )
                max_ts = self._timestamp_of_max_angle_in_frame(
                    timestamp1=frame_start,
                    timestamp2=frame_end,
                    min_distance_to_camera=min_distance_to_camera,
                )
                frame[self.__class__.TIMESTAMP_OF_MIN_ANGLE] = min_ts
                frame[self.__class__.TIMESTAMP_OF_MAX_ANGLE] = max_ts
                frame[self.__class__.DISTANCE_BETWEEN_POSITIONS] = self._distance_between_positions(min_ts, max_ts) # pylint: disable=C0301
                frame[self.__class__.ANGLE_BETWEEN_POSITIONS] = self._angle_between_timestamps(min_ts, max_ts) # pylint: disable=C0301
            self._frames.append(frame)
            frame_start = frame_end

            if frame_end is None or len(self._frames) == limit:
                break

        return self._frames

    def get_complete_frames_where_range_exceeds_threshold(
            self,
            threshold_rad,
            min_distance_to_camera,
            limit=None,
    ):
        return [
            frame for frame in self.get_frames_where_range_exceeds_threshold(
                threshold_rad=threshold_rad,
                min_distance_to_camera=min_distance_to_camera,
                limit=limit,
            )
            if self.is_not_terminal_frame(frame)
        ]


    # Frame helper methods

    def get_early_position(self, frame):
        if self.is_terminal_frame(frame):
            return None

        return self.tag.get_position_at_timestamp(self.get_early_min_max_timestamp(frame))

    def get_late_position(self, frame):
        if self.is_terminal_frame(frame):
            return None

        return self.tag.get_position_at_timestamp(self.get_late_min_max_timestamp(frame))

    def get_early_min_max_timestamp(self, frame):
        if frame[self.__class__.TIMESTAMP_OF_MIN_ANGLE] < frame[self.__class__.TIMESTAMP_OF_MAX_ANGLE]: # pylint: disable:C0301
            return frame[self.__class__.TIMESTAMP_OF_MIN_ANGLE]
        else:
            return frame[self.__class__.TIMESTAMP_OF_MAX_ANGLE]

    def get_late_min_max_timestamp(self, frame):
        if frame[self.__class__.TIMESTAMP_OF_MIN_ANGLE] > frame[self.__class__.TIMESTAMP_OF_MAX_ANGLE]: # pylint: disable:C0301
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
