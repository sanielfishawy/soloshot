# pylint: disable=C0413
import sys
import os
sys.path.insert(0, os.getcwd())

from geo_mapping.geo_mapper import MapCoordinateTransformer

class Tag:
    '''
    Tag object with latitude, longitude, and time series. It also accepts a
    MapCoordinateTransformer to report position in x, y coordinates on a tkinter
    canvas.

    Tries to conform to the same api as ViewableObject so that it may be used with
    calibration pipeline tools like TagPositionAnalyzer.
    '''

    def __init__(
            self,
            latitude_series,
            longitude_series,
            time_series,
            alignment_offset_video_to_tag_ms: int = None,
            map_coordinate_transformer: MapCoordinateTransformer = None,
    ):
        # params
        self._latitude_series = latitude_series
        self._longitude_series = longitude_series
        self._time_series = time_series
        self._alignment_offset_video_to_tag_ms = alignment_offset_video_to_tag_ms

        if self._alignment_offset_video_to_tag_ms is None:
            # Emperical: see tag_gps_timebase_alignment_all_direction_changes.yml
            self._alignment_offset_video_to_tag_ms = -57

        self._map_coordinate_transformer = map_coordinate_transformer

        # lazy init
        self._normalized_time_series = None
        self._xy_position_series = None


    # compatability with ViewableObject and simulated calibation pipeline
    def get_num_timestamps(self):
        return self._latitude_series.size

    # compatability with ViewableObject and simulated calibation pipeline
    def get_position_at_timestamp(self, timestamp):
        return self.get_x_y_postion_at_timestamp(timestamp)

    # compatability with ViewableObject and simulated calibation pipeline
    def get_position_history(self):
        return self.get_xy_position_series()

    def get_xy_position_series(self):
        if self._xy_position_series is None:
            self._xy_position_series = [
                self.get_x_y_postion_at_timestamp(timestamp) for timestamp
                in range(self.get_num_timestamps())
            ]
        return self._xy_position_series

    def get_x_y_postion_at_timestamp(self, timestamp):
        return (
            self.get_x_position_at_timestamp(timestamp),
            self.get_y_position_at_timestamp(timestamp),
        )

    def get_x_position_at_timestamp(self, timestamp):
        self._ensure_map_coordinate_transformer()
        return self._map_coordinate_transformer.get_x_for_longitude(
            self._longitude_series[timestamp]
        )

    def get_y_position_at_timestamp(self, timestamp):
        self._ensure_map_coordinate_transformer()
        return self._map_coordinate_transformer.get_y_for_latitude(
            self._latitude_series[timestamp]
        )

    def get_lat_long_at_timestamp(self, timestamp):
        return (
            self._latitude_series[timestamp],
            self._longitude_series[timestamp]
        )

    def get_idx_after_tag_time(self, tag_time_ms):
        for idx, time in enumerate(self._get_normalized_time_series()):
            if time >= tag_time_ms:
                return idx
        return self._time_series.size - 1

    def get_idx_before_tag_time(self, tag_time_ms):
        for idx, time in enumerate(self._get_normalized_time_series()):
            if time >= tag_time_ms:
                return max(0, idx - 1)
        return 0

    def get_tag_time_for_timestamp(self, timestamp):
        return self._get_normalized_time_series()[timestamp]

    def get_video_time_for_tag_time(self, tag_time):
        return tag_time - self._alignment_offset_video_to_tag_ms

    def get_video_time_for_timestamp(self, timestamp):
        return self.get_video_time_for_tag_time(self.get_tag_time_for_timestamp(timestamp))

    def get_tag_time_for_video_time(self, video_time):
        return video_time + self._alignment_offset_video_to_tag_ms

    def get_idx_after_video_time(self, video_time_ms):
        return self.get_idx_after_tag_time(self.get_tag_time_for_video_time(video_time_ms))

    def get_idx_before_video_time(self, video_time_ms):
        return self.get_idx_before_tag_time(self.get_tag_time_for_video_time(video_time_ms))

    def _get_normalized_time_series(self):
        if self._normalized_time_series is None:
            self._normalized_time_series = self._time_series - self._time_series[0]
        return self._normalized_time_series

    def _ensure_map_coordinate_transformer(self):
        assert self._map_coordinate_transformer is not None,\
               'MapCoordinateTransformer required to calculate x, y positions'
