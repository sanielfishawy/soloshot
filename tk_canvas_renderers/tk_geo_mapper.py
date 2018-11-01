# pylint: disable=C0413
import sys
import os
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np

sys.path.insert(0, os.getcwd())
from geo_mapping.geo_mapper import MapFitter, MapCoordinateTransformer

class TkGeoMapper:
    '''
    Given a latitude and longitude series describing a track.
    Fetches a map that fits the data. Adds the map to a canvas. Draws
    the track on the canvas overlaying the map.

    This was used for MapFitter images and other geo mapper classes.

    Look at GeoMapScrubber for a more useful widget that allows scrubbing
    forward and backward on a track in a map.
    '''
    def __init__(self,
                 latitude_series: np.ndarray,
                 longitude_series: np.ndarray,
                 marker_positions=None,
                 track_color='red'
                ):

        self._latitude_series = latitude_series
        self._longitude_series = longitude_series
        self._marker_positions = marker_positions
        self._track_color = track_color

        if self._marker_positions is None:
            self._add_markers = False
        else:
            self._add_markers = True

        assert self._latitude_series.size == self._longitude_series.size, \
               (f'latitude_series ({self._latitude_series.size}) '
                f'must be same size as longitude_series ({self._longitude_series.size})')

        self._map_fitter = MapFitter(self._latitude_series,
                                     self._longitude_series,
                                     add_markers=self._add_markers,
                                    )

        self._map_coordinate_transformer = \
            MapCoordinateTransformer(self._map_fitter.get_center_latitude(),
                                     self._map_fitter.get_center_longitude(),
                                     self._map_fitter.get_map_scaled_width(),
                                     self._map_fitter.get_map_scaled_height(),
                                     self._map_fitter.get_zoom(),
                                     self._map_fitter.get_scale(),
                                    )

        # laxy init
        self._root = None
        self._canvas = None
        self._map_on_canvas = None
        self._map_image = None
        self._x_y_series = None
        self._x_y_series_flattened = None

    def _setup_ui(self):
        self._root = tk.Tk()

        self._canvas = tk.Canvas(master=self._root,
                                 width=self._map_fitter.get_map_scaled_width(),
                                 height=self._map_fitter.get_map_scaled_height(),
                                )
        self._canvas.grid(row=0, column=0)
        self._map_on_canvas = self._canvas.create_image(0, 0, anchor='nw')

        self._canvas.itemconfig(self._map_on_canvas, image=self._get_map_image())

        self._canvas.create_line(*self._get_x_y_series_flattened(),
                                 fill=self._track_color,
                                )

        self._add_marker_dots()


    def _add_marker_dots(self):
        if self._marker_positions is not None:
            for position in self._marker_positions:
                y = self._map_coordinate_transformer.get_y_for_latitude(position[0])
                x = self._map_coordinate_transformer.get_x_for_longitude(position[1])
                self._canvas.create_oval(x-2, y-2, x+2, y+2, fill='blue')

    def _get_map_image(self):
        if self._map_image is None:
            self._map_image = ImageTk.PhotoImage(Image.open(self._map_fitter.get_map()))
        return self._map_image

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

    def run(self):
        self._setup_ui()
        self._root.mainloop()
        return self
