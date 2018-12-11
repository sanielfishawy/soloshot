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
            base_gps_time_series: np.ndarray = None,
            base_gps_error_circle_radius_feet=15,
            pan_motor_angle_series: np.ndarray = None,
            base_motor_time_series: np.ndarray = None,
            alignment_offset_motor_to_video_ms=None,
            map_coordinate_transformer: MapCoordinateTransformer = None,
    ):
        self._actual_latitude = actual_latitude
        self._actual_longitude = actual_longitude
        self._calibrated_latitude = calibrated_latitude
        self._calibrated_longitude = calibrated_longitude
        self._base_gps_time_series = base_gps_time_series
        self._base_error_circle_radius_feet = base_gps_error_circle_radius_feet
        self._pan_motor_angle_series = pan_motor_angle_series
        self._base_motor_time_series = base_motor_time_series
        self._gps_latitude_series = gps_latitude_series
        self._gps_longitude_series = gps_longitude_series
        self._alignment_offset_motor_to_video_ms = alignment_offset_motor_to_video_ms
        self._map_coordinate_transformer = map_coordinate_transformer

        # Emperical see: pan_motor_timebase_alignment.yml
        if self._alignment_offset_motor_to_video_ms is None:
            self._alignment_offset_motor_to_video_ms = 200

        # lazy inits for performance
        self._normalized_base_motor_time_series = None
        self._base_motor_time_series_in_video_time = None
        self._pan_motor_angle_series_rad = None


    #
    # GPS methods
    #

    # For compatability with calibration pipeline base on simulated Camera
    def get_base_gps_error_circle_radius_feet(self):
        return self._base_error_circle_radius_feet

    def get_base_gps_error_circle_radius_pixels(self):
        return self._base_error_circle_radius_feet / \
               self._get_map_coordinate_transformer().get_feet_per_px()

    def get_gps_position(self):
        return self.get_x_y_gps_position()

    def get_x_y_gps_position(self):
        return (
            self.get_x_gps_position(),
            self.get_y_gps_position(),
        )

    def get_actual_x_y_position(self):
        return (
            self._get_map_coordinate_transformer().get_x_for_longitude(self._actual_longitude),
            self._get_map_coordinate_transformer().get_y_for_latitude(self._actual_latitude),
        )

    def get_gps_latitude(self):
        return self._gps_latitude_series[0]

    def get_gps_longitude(self):
        return self._gps_longitude_series[0]

    def get_x_gps_position(self):
        return self._get_map_coordinate_transformer().get_x_for_longitude(self.get_gps_longitude())

    def get_y_gps_position(self):
        return self._get_map_coordinate_transformer().get_y_for_latitude(self.get_gps_latitude())

    def _get_map_coordinate_transformer(self):
        assert self._map_coordinate_transformer is not None, \
               'Must provide a MapCoordinateTransformer to get x, y pixel positions'
        return self._map_coordinate_transformer

    #
    # Motor methods
    #


    def get_normalized_base_motor_time_series(self):
        if self._normalized_base_motor_time_series is None:
            self._normalized_base_motor_time_series = self._base_motor_time_series - self._base_motor_time_series[0]
        return self._normalized_base_motor_time_series

    def get_base_motor_time_series_in_video_time(self):
        if self._base_motor_time_series_in_video_time is None:
            self._base_motor_time_series_in_video_time = self.get_normalized_base_motor_time_series() +\
                                                   self._alignment_offset_motor_to_video_ms
        return self._base_motor_time_series_in_video_time

    def get_motor_time_for_video_time(self, video_time_ms):
        return video_time_ms - self._alignment_offset_motor_to_video_ms

    def get_idx_after_video_time(self, video_time):
        for idx, v_time in enumerate(self.get_base_motor_time_series_in_video_time()):
            if v_time > video_time:
                return idx
        return None

    def get_idx_before_video_time(self, video_time):
        after = self.get_idx_after_video_time(video_time)
        if after is None:
            return None
        return after - 1

    def get_idx_after_motor_time(self, motor_time):
        for idx, m_time in enumerate(self.get_normalized_base_motor_time_series()):
            if m_time > motor_time:
                return idx
        return None

    def get_idx_before_motor_time(self, motor_time):
        after = self.get_idx_after_motor_time(motor_time)
        if after is None:
            return None
        return after - 1

    def get_pan_motor_angle_series_rad(self):
        if self._pan_motor_angle_series_rad is None:
            self._pan_motor_angle_series_rad = np.radians(self._pan_motor_angle_series)
        return self._pan_motor_angle_series_rad

    def get_motor_angle_for_video_time_rad(self, video_time):
        return np.interp(
            x=video_time,
            xp=self.get_base_motor_time_series_in_video_time(),
            fp=self.get_pan_motor_angle_series_rad(),
        )
