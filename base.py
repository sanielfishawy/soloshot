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
            gps_latitude,
            gps_longitude,
            actual_latitude=None,
            actual_longitude=None,
            pan_motor_angle_series: np.ndarray = None,
            base_time_series: np.ndarray = None,
            map_coordinate_transformer: MapCoordinateTransformer = None,
    ):
        self._actual_latitude = actual_latitude
        self._actual_longitude = actual_longitude
        self._pan_motor_angle_series = pan_motor_angle_series
        self._base_time_series = base_time_series
        self._gps_latitude = gps_latitude
        self._gps_longitude = gps_longitude
        self._map_coordinate_transformer = map_coordinate_transformer

    # For compatability with calibration pipeline base on simulated Camera
    def get_gps_position(self):
        return self.get_x_y_gps_position()

    def get_x_y_gps_position(self):
        return (
            self.get_x_gps_position(),
            self.get_y_gps_position(),
        )

    def get_x_gps_position(self):
        self._ensure_map_coordinate_transformer()
        return self._map_coordinate_transformer.get_x_for_longitude(self._gps_longitude)

    def get_y_gps_position(self):
        self._ensure_map_coordinate_transformer()
        return self._map_coordinate_transformer.get_y_for_latitude(self._gps_latitude)

    def _ensure_map_coordinate_transformer(self):
        assert self._map_coordinate_transformer is not None, \
               'Must provide a MapCoordinateTransformer to get x, y pixel positions'
