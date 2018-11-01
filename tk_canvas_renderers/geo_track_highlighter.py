# pylint: disable=C0413
import sys
import os
import tkinter as tk
import numpy as np

sys.path.insert(0, os.getcwd())
from geo_mapping.geo_mapper import MapCoordinateTransformer

class GeoTrackHighlighter:
    '''
    Receives latitude and longitude series as inputs as well as a canvas.
    Draws the track represented by the series on the canvas. Allows you to highlight
    a point on the track.
    '''

    def __init__(
            self,
            canvas: tk.Canvas,
            latitude_series: np.ndarray,
            longitude_series: np.ndarray,
            map_coordinate_transformer: MapCoordinateTransformer,
            track_color='orange',
            track_head_color='red',
    ):
        self._canvas = canvas
        self._latitude_series = latitude_series
        self._longitude_series = longitude_series
        self._map_coordinate_transformer = map_coordinate_transformer
        self._track_color = track_color
        self._highlight_color = track_head_color

        self._highlighted_idx = 0

        # lazy inits
        self._x_y_series = None
        self._x_y_series_flattened = None

        self._track_line = None
        self._highlight_dot = None

    def setup_ui(self):
        self._track_line = self._canvas.create_line(
            *self._get_x_y_series_flattened(),
            fill=self._track_color,
        )
        return self

    def set_highlight_idx(self, idx: int):
        assert idx >= 0 and idx < self._latitude_series.size
        self._highlighted_idx = idx
        self._display_highlight_dot()

    def _display_highlight_dot(self):
        dot_size = 3
        if self._highlight_dot is not None:
            self._canvas.delete(self._highlight_dot)

        x = self._get_x_y_series()[self._highlighted_idx][0]
        y = self._get_x_y_series()[self._highlighted_idx][1]
        self._highlight_dot = self._canvas.create_oval(
            x - dot_size,
            y - dot_size,
            x + dot_size,
            y + dot_size,
            fill=self._highlight_color,
            outline=self._highlight_color,
        )
        self._canvas.update()

    def _get_x_y_series(self):
        if self._x_y_series is None:
            r = []
            for idx in range(self._latitude_series.size):
                x = self._map_coordinate_transformer.get_x_for_longitude(self._longitude_series[idx]) # pylint: disable=C0301
                y = self._map_coordinate_transformer.get_y_for_latitude(self._latitude_series[idx])
                r.append([x, y])
            self._x_y_series = r
        return self._x_y_series

    def _get_x_y_series_flattened(self):
        if self._x_y_series_flattened is None:
            self._x_y_series_flattened = [item for sublist in self._get_x_y_series() for item in sublist] # pylint: disable=C0301
        return self._x_y_series_flattened
