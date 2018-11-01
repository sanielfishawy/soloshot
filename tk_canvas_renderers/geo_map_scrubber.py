# pylint: disable=C0413
import sys
import os
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

sys.path.insert(0, os.getcwd())
from tk_canvas_renderers.tk_geo_mapper import TkGeoMapper
from tk_canvas_renderers.scrollable_canvas import ScrollableCanvas
from tk_canvas_renderers.video_postion_indicator import VideoPositionIndicator
from geo_mapping.geo_mapper import MapFitter

class GeoMapScrubber:
    '''Visualizes a geo map with a track. A slider (VideoPositionIndicator) allows you
       to scrub back and forth along the track'''

    def __init__(
            self,
            latitude_series: np.ndarray,
            longitude_series: np.ndarray,
            width=800,
            height=400,
            track_color='orange',
            track_head_color='red',
    ):
        self._latitude_series = latitude_series
        self._longitude_series = longitude_series
        self._width = width
        self._height = height
        self._track_color = track_color
        self._track_head_color = track_head_color

        # lazy inits
        self._slider_canvas = None
        self._slider = None
        self._map_image = None
        self._scrollable_canvas_obj = None
        self._map_canvas = None
        self._map_frame = None
        self._map_on_canvas = None

    def get_ui(self, master):

        self._slider_canvas = tk.Canvas(
            master=master,
            width=self._width,
            height=30,
        )
        self._slider_canvas.grid(row=0, column=0)

        self._slider = VideoPositionIndicator(
            self._slider_canvas,
            50,
        ).setup_ui()

        self._scrollable_canvas_obj = ScrollableCanvas(
            master,
            self._get_map_image().width(),
            self._get_map_image().height(),
            self._width,
            self._height,
        ).setup_ui()

        self._map_frame = self._scrollable_canvas_obj.get_frame()
        self._map_frame.grid(row=1, column=0)

        self._map_canvas = self._scrollable_canvas_obj.get_canvas()
        self._map_on_canvas = self._map_canvas.create_image(0, 0, anchor='nw')
        self._map_canvas.itemconfig(self._map_on_canvas, image=self._get_map_image())

    def _get_map_image(self):
        if self._map_image is None:
            map_path = MapFitter(self._latitude_series, self._longitude_series).get_map()
            self._map_image = ImageTk.PhotoImage(Image.open(map_path))
        return self._map_image

    def run(self):
        master = tk.Tk()
        self.get_ui(master)
        master.mainloop()
