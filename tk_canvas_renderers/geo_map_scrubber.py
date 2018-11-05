# pylint: disable=C0413
import sys
import os
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

sys.path.insert(0, os.getcwd())
from tk_canvas_renderers.scrollable_canvas import ScrollableCanvas
from tk_canvas_renderers.video_postion_indicator import VideoPositionIndicator
from tk_canvas_renderers.slider_mouse_handler import SliderMouseHandler
from tk_canvas_renderers.geo_track_highlighter import GeoTrackHighlighter
from tk_canvas_renderers.tabular_data import TabularData
from geo_mapping.geo_mapper import MapFitter, MapCoordinateTransformer

class GeoMapScrubber:
    '''Visualizes a geo map with a track. A slider (VideoPositionIndicator) allows you
       to scrub back and forth along the track'''

    def __init__(
            self,
            latitude_series: np.ndarray,
            longitude_series: np.ndarray,
            time_series: np.ndarray,
            width=700,
            height=700,
            track_color='orange',
            track_head_color='red',
    ):
        self._latitude_series = latitude_series
        self._longitude_series = longitude_series
        self._time_series = time_series
        self._width = width
        self._height = height
        self._track_color = track_color
        self._track_head_color = track_head_color

        # lazy inits
        self._map_fitter = None
        self._map_coordinate_transformer = None

        # tk widgets
        self._tabular_info_frame = None
        self._tablular_info = None
        self._slider_canvas = None
        self._slider = None
        self._slider_mouse_handler = None
        self._map_image = None
        self._scrollable_canvas_obj = None
        self._map_canvas = None
        self._map_frame = None
        self._map_on_canvas = None
        self._geo_track_hilighter = None

    def setup_ui(self, master):
        self._tabular_info_frame = tk.Frame(master=master)
        self._tabular_info_frame.grid(
            column=0,
            row=0,
            sticky=tk.W
        )
        self._tablular_info = TabularData(data=self._get_tabular_info())
        self._tablular_info.setup_ui(master=self._tabular_info_frame)


        slider_margin_pixels = 50
        self._slider_canvas = tk.Canvas(
            master=master,
            width=self._width,
            height=30,
        )
        self._slider_canvas.grid(row=1, column=0)

        self._slider = VideoPositionIndicator(
            self._slider_canvas,
            slider_margin_pixels,
        ).setup_ui()

        self._slider_mouse_handler = SliderMouseHandler(
            canvas=self._slider_canvas,
            margin_pixels=slider_margin_pixels,
            num_points=self._latitude_series.size,
            position_idx_callback=self._slider_mouse_handler_position_callback,
            selected_idx_callback=self._slider_mouse_handler_selected_callback,
        )

        self._scrollable_canvas_obj = ScrollableCanvas(
            master,
            self._get_map_image().width(),
            self._get_map_image().height(),
            self._width,
            self._height,
        ).setup_ui()

        self._map_frame = self._scrollable_canvas_obj.get_frame()
        self._map_frame.grid(
            row=2,
            column=0,
        )

        self._map_canvas = self._scrollable_canvas_obj.get_canvas()
        self._map_on_canvas = self._map_canvas.create_image(0, 0, anchor='nw')
        self._map_canvas.itemconfig(self._map_on_canvas, image=self._get_map_image())

        self._geo_track_hilighter = GeoTrackHighlighter(
            self._map_canvas,
            self._latitude_series,
            self._longitude_series,
            self._get_map_coordinate_transformer(),
        ).setup_ui()

    def _get_map_image(self) -> ImageTk.PhotoImage:
        if self._map_image is None:
            map_path = self._get_map_fitter().get_map()
            self._map_image = ImageTk.PhotoImage(Image.open(map_path))
        return self._map_image

    def _get_map_fitter(self) -> MapFitter:
        if self._map_fitter is None:
            self._map_fitter = MapFitter(self._latitude_series, self._longitude_series)
        return self._map_fitter

    def _get_map_coordinate_transformer(self) -> MapCoordinateTransformer:
        if self._map_coordinate_transformer is None:
            self._map_coordinate_transformer = MapCoordinateTransformer(
                self._get_map_fitter().get_center_latitude(),
                self._get_map_fitter().get_center_longitude(),
                self._get_map_fitter().get_map_scaled_width(),
                self._get_map_fitter().get_map_scaled_height(),
                self._get_map_fitter().get_zoom(),
                self._get_map_fitter().get_scale(),
            )
        return self._map_coordinate_transformer

    def _slider_mouse_handler_position_callback(self, idx):
        self._slider.set_percent(percent=self._get_percent_from_idx(idx))
        self._geo_track_hilighter.set_highlight_idx(idx)
        self._tablular_info.update_values(
            self._get_tabular_info(
                idx=idx,
                time=self._get_time_from_idx(idx),
            )
        )

    def _slider_mouse_handler_selected_callback(self, idx):
        self._slider.set_selected(percent=self._get_percent_from_idx(idx))
        self._tablular_info.update_values(
            self._get_tabular_info(
                selected_idx=idx,
                selected_time=self._get_time_from_idx(idx),
            )
        )
        self._geo_track_hilighter.set_selected_idx(idx)

    def _get_percent_from_idx(self, idx):
        return idx / (self._latitude_series.size - 1)

    def _get_time_from_idx(self, idx):
        return self._time_series[idx] - self._time_series[0]

    def _get_tabular_info(self, idx=None, time=None, selected_idx=None, selected_time=None):
        return [
            {
                TabularData.LABEL: 'Index:',
                TabularData.VALUE: idx,
            },
            {
                TabularData.LABEL: 'Time:',
                TabularData.VALUE: time,
            },
            {
                TabularData.LABEL: 'Selected Index:',
                TabularData.VALUE: selected_idx,
                TabularData.COLUMN: 1,
            },
            {
                TabularData.LABEL: 'Selected Time:',
                TabularData.VALUE: selected_time,
                TabularData.COLUMN: 1,
            },
        ]


    def run(self):
        master = tk.Tk()
        self.setup_ui(master)
        master.mainloop()
