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

        #state
        self._highlighted_idx = 0
        self._previous_highligthed_idx = 0

        # lazy inits
        self._x_y_series = None
        self._x_y_series_flattened = None

        self._track_line = None
        self._highlight_dot = None
        self._highlight_tail = None
        self._selected_circle = None

        # constants
        self._dot_radius = 5
        self._tail_width = 3
        self._selected_circle_color = 'cyan'
        self._selected_circle_radius = 6
        self._selected_circle_width = 2

    def setup_ui(self):
        self._track_line = self._canvas.create_line(
            *self._get_x_y_series_flattened(),
            fill=self._track_color,
        )

        self._highlight_dot = self._canvas.create_oval(
            self._get_oval_coords(
                idx=self._highlighted_idx,
                radius=self._dot_radius,
            ),
            fill=self._highlight_color,
            outline=self._highlight_color,
        )

        self._highlight_tail = self._canvas.create_line(
            self._get_tail_coords(),
            fill=self._highlight_color,
            width=self._tail_width,
        )

        self._canvas.update()
        return self

    def set_highlight_idx(self, idx: int):
        self._assert_idx_in_bounds(idx)
        self._previous_highligthed_idx = self._highlighted_idx
        self._highlighted_idx = idx
        self._move_highlight_dot()
        self._move_highlight_tail()

    def set_selected_idx(self, idx: int):
        self._assert_idx_in_bounds(idx)
        if self._selected_circle is None:
            self._selected_circle = self._canvas.create_oval(
                self._get_oval_coords(
                    idx=idx,
                    radius=self._selected_circle_radius,
                ),
                outline=self._selected_circle_color,
                width=self._selected_circle_width,
            )
        self._canvas.coords(
            self._selected_circle,
            self._get_oval_coords(
                idx=idx,
                radius=self._selected_circle_radius,
            ),
        )

    def _assert_idx_in_bounds(self, idx):
        assert idx >= 0 and idx < self._latitude_series.size

    def _move_highlight_dot(self):
        self._canvas.coords(
            self._highlight_dot,
            self._get_oval_coords(
                idx=self._highlighted_idx,
                radius=self._dot_radius,
            ),
        )

    def _move_highlight_tail(self):
        self._canvas.coords(
            self._highlight_tail,
            self._get_tail_coords(),
        )

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

    def _get_x_y_from_idx(self, idx):
        return (
            self._get_x_y_series()[idx][0],
            self._get_x_y_series()[idx][1],
        )

    def _get_tail_coords(self):
        x_1, y_1 = self._get_x_y_from_idx(self._highlighted_idx)
        if self._previous_highligthed_idx < self._highlighted_idx:
            x_2, y_2 = self._get_x_y_from_idx(self._highlighted_idx - 1)
        elif self._previous_highligthed_idx > self._highlighted_idx:
            x_2, y_2 = self._get_x_y_from_idx(self._highlighted_idx + 1)
        else:
            x_2, y_2 = (x_1, y_1)

        return [x_1, y_1, x_2, y_2]

    def _get_oval_coords(self, idx, radius):
        x, y = self._get_x_y_from_idx(idx)
        return [
            x - radius,
            y - radius,
            x + radius,
            y + radius,
        ]
