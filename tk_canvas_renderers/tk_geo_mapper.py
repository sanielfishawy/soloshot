# pylint: disable=C0413
import sys
import os
import tkinter as tk
from PIL import Image, ImageTk

sys.path.insert(0, os.getcwd())
from geo_mapping.geo_mapper import MapFitter

class TkGeoMapper:
    def __init__(self,
                 latitude_series,
                 longitude_series,
                ):

        self._latitude_series = latitude_series
        self._longitude_series = longitude_series

        self._map_fitter = MapFitter(self._latitude_series,
                                     self._longitude_series,
                                    )

        # laxy init
        self._root = None
        self._canvas = None
        self._map_on_canvas = None
        self._map_image = None

    def _setup_ui(self):
        self._root = tk.Tk()

        self._canvas = tk.Canvas(master=self._root,
                                 width=self._map_fitter.get_map_scaled_width(),
                                 height=self._map_fitter.get_map_scaled_height(),
                                )
        self._canvas.grid(row=0, column=0)
        self._map_on_canvas = self._canvas.create_image(0, 0, anchor='nw')

        self._canvas.itemconfig(self._map_on_canvas, image=self._get_map_image())

    def _get_map_image(self):
        if self._map_image is None:
            self._map_image = ImageTk.PhotoImage(Image.open(self._map_fitter.get_map()))
        return self._map_image

    def run(self):
        self._setup_ui()
        self._root.mainloop()
        return self
