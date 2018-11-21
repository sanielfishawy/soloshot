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
        self._map_coordinate_transformer = map_coordinate_transformer

        # lazy inits for speed
        self._mean_gps_latitude = None
        self._mean_gps_longitude = None

    # For compatability with calibration pipeline base on simulated Camera
    def get_gps_position(self):
        return self.get_x_y_gps_position()

    def get_x_y_gps_position(self):
        return (
            self.get_x_gps_position(),
            self.get_y_gps_position(),
        )

    def get_mean_gps_latitude(self):
        if self._mean_gps_latitude is None:
            self._mean_gps_latitude = np.mean(self._gps_latitude_series)
        return self._mean_gps_latitude

    def get_mean_gps_longitude(self):
        if self._mean_gps_longitude is None:
            self._mean_gps_longitude = np.mean(self._gps_longitude_series)
        return self._mean_gps_longitude

    def get_x_gps_position(self):
        self._ensure_map_coordinate_transformer()
        return self._map_coordinate_transformer.get_x_for_longitude(self.get_mean_gps_longitude())

    def get_y_gps_position(self):
        self._ensure_map_coordinate_transformer()
        return self._map_coordinate_transformer.get_y_for_latitude(self.get_mean_gps_latitude())

    def _ensure_map_coordinate_transformer(self):
        assert self._map_coordinate_transformer is not None, \
               'Must provide a MapCoordinateTransformer to get x, y pixel positions'
