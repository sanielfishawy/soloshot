# pylint: disable=C0413
import os
import sys
from typing import List
import tkinter as tk

sys.path.insert(0, os.getcwd())
from tk_canvas_renderers.single_image_canvas import SingleImageCanvas
from video_and_photo_tools.image_from_video import ImageFromVideo


class VerticalImageList:

    def __init__(self, images_from_video: List[ImageFromVideo],
                 window_height=None,
                ):

        self._images_from_video = images_from_video
        self._window_height = window_height

        self._root = None
        self._outer_frame = None
        self._outer_canvas = None
        self._vbar = None
        self._single_image_canvases = None

    def _setup_ui(self):
        self._root = tk.Tk()
        self._root.title(self._images_from_video[0].get_video_path().resolve())

        self._outer_frame = tk.Frame(self._root)
        self._outer_frame.grid(row=0, column=0)

        self._outer_canvas = tk.Canvas(self._outer_frame,
                                       scrollregion=(0,
                                                     0,
                                                     self._get_image_width(),
                                                     self._get_total_images_height()),
                                       background='blue')
        self._outer_canvas.config(width=self._get_image_width(),
                                  height=self._get_window_height())

        self._vbar = tk.Scrollbar(self._outer_frame, orient=tk.VERTICAL)
        self._vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._vbar.config(command=self._outer_canvas.yview)

        self._outer_canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self._outer_canvas.config(yscrollcommand=self._vbar.set)

        self._add_inner_canvases()

    def _add_inner_canvases(self):
        y_pos = 0
        for sic in self._get_single_image_canvases():
            self._outer_canvas.create_window(0, y_pos,
                                             anchor='nw',
                                             height=sic.get_height(),
                                             width=sic.get_width(),
                                             window=sic.get_canvas())

            y_pos += sic.get_height()

    def _get_single_image_canvases(self) -> List[SingleImageCanvas]:
        if self._single_image_canvases is None:
            self._single_image_canvases = [SingleImageCanvas(self._outer_canvas, ifv)
                                           for ifv
                                           in self._images_from_video]
        return self._single_image_canvases

    def _get_window_height(self):
        if self._window_height is None:
            self._window_height = self._root.winfo_screenheight() - 75
        return self._window_height

    def _get_image_width(self):
        return self._get_single_image_canvases()[0].get_width()

    def _get_image_height(self):
        return self._get_single_image_canvases()[0].get_height()

    def _get_total_images_height(self):
        return self._get_num_images() * self._get_image_height()

    def _get_num_images(self):
        return len(self._images_from_video)

    def run(self):
        self._setup_ui()
        self._root.mainloop()
