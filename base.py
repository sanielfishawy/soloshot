# pylint: disable=C0413
import sys
import os
import numpy as np
sys.path.insert(0, os.getcwd())

from geo_mapping.geo_mapper import MapCoordinateTransformer

class Base:
    '''
    Compatable with legacy data pipeline.
    Camera was used for simiulated camera including pan angle etc.

    Base has pan_motor_angle_series, gps_position, actual_postion

    The intention is to make Base and Lens compatible with the calibration pipline that was tested
    in simulation with Camera.
    '''

    def __init__(
            self,
            gps_latitude_series,
            gps_longitude_series,
            actual_latitude=None,
            actual_longitude=None,
            calibrated_latitude=None,
            calibrated_longitude=None,
            pan_motor_angle_series: np.ndarray = None,
            base_time_series: np.ndarray = None,
            alignment_offset_motor_to_video_ms = None,
            map_coordinate_transformer: MapCoordinateTransformer = None,
    ):
        self._actual_latitude = actual_latitude
        self._actual_longitude = actual_longitude
        self._calibrated_latitude = calibrated_latitude
        self._calibrated_longitude = calibrated_longitude
        self._pan_motor_angle_series = pan_motor_angle_series
        self._base_time_series = base_time_series
        self._gps_latitude_series = gps_latitude_series
        self._gps_longitude_series = gps_longitude_series,
        self._alignment_offset_motor_to_video_ms = alignment_offset_motor_to_video_ms
        self._map_coordinate_transformer = map_coordinate_transformer

        # Emperical see: pan_motor_timebase_alignment.yml
        if self._alignment_offset_motor_to_video_ms is None:
            self._alignment_offset_motor_to_video_ms = 206

        # lazy inits for performance
        self._normalized_base_time_series = None


    #
    # GPS methods
    #

    # For compatability with calibration pipeline base on simulated Camera
    def get_gps_position(self):
        return self.get_x_y_gps_position()

    def get_x_y_gps_position(self):
        return (
            self.get_x_gps_position(),
            self.get_y_gps_position(),
        )

    def get_gps_latitude(self):
        return self._gps_latitude_series[0]

    def get_gps_longitude(self):
        return self._gps_longitude_series[0]

    def get_x_gps_position(self):
        self._ensure_map_coordinate_transformer()
        return self._map_coordinate_transformer.get_x_for_longitude(self.get_gps_longitude())

    def get_y_gps_position(self):
        self._ensure_map_coordinate_transformer()
        return self._map_coordinate_transformer.get_y_for_latitude(self.get_gps_latitude())

    def _ensure_map_coordinate_transformer(self):
        assert self._map_coordinate_transformer is not None, \
               'Must provide a MapCoordinateTransformer to get x, y pixel positions'

    #
    # Motor methods
    #

    def get_normalized_base_time_series(self):
        if self._normalized_base_time_series is None:
            self._normalized_base_time_series = self._base_time_series - self._base_time_series[0]
        return self._normalized_base_time_series

    def get_motor_time_for_video_time(self, video_time_ms):
        return video_time_ms - self._alignment_offset_motor_to_video_ms

    def get_motor_idx_for_motor_time(self, motor_time):
        idx = None
        for i, time_ms in enumerate(list(self.get_normalized_base_time_series())):
            if time_ms > motor_time:
                idx = i
                break

        after_idx = idx
        before_idx = idx - 1
        after_time = self.get_normalized_base_time_series()[after_idx]
        before_time = self.get_normalized_base_time_series()[before_idx]
        if abs(before_time - motor_time) < abs(after_time - motor_time):
            return before_idx
        return after_idx

    def get_motor_idx_for_video_time(self, video_time):
        return self.get_motor_idx_for_motor_time(
            motor_time=self.get_motor_time_for_video_time(video_time)
        )

    def get_motor_angle_for_video_time(self, video_time):
        return self._pan_motor_angle_series[
            self.get_motor_idx_for_video_time(video_time)
        ]
