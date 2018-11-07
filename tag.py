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
            map_coordinate_transformer: MapCoordinateTransformer = None,
    ):
        self._latitude_series = latitude_series
        self._longitude_series = longitude_series
        self._time_series = time_series
        self._map_coordinate_transformer = map_coordinate_transformer

    def get_position_at_timestamp(self, timestamp):
        return self.get_x_y_postion_at_timestamp(timestamp)

    def get_x_y_postion_at_timestamp(self, timestamp):
        self._ensure_map_coordinate_transformer()
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

    def _ensure_map_coordinate_transformer(self):
        assert self._map_coordinate_transformer is not None,\
               'MapCoordinateTransformer required to calculate x, y positions'
