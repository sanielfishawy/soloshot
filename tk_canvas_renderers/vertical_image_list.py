from typing import Iterable
import tkinter as tk
import PIL.ImageTk
import PIL.Image

from tk_canvas_renderers.canvas_utils import CanvasUtils

class VerticalImageList:

    def __init__(self, images_from_video: Iterable[PIL.Image.Image],
                 window_height=None,
                ):

        self._images_from_video = images_from_video
        self._tk_images = None
        self._window_height = window_height

        self._root = None
        self._outer_frame = None
        self._outer_canvas = None
        self._vbar = None
        self._inner_canvases = []

    def _setup_ui(self):
        self._root = tk.Tk()

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
        for photo in self._get_tk_photos():
            inner_canvas = tk.Canvas(master=self._outer_canvas,
                                     bg=CanvasUtils.random_color()
                                    )
            inner_canvas.create_image(0, 0, image=photo, anchor='nw')
            self._outer_canvas.create_window(0, y_pos,
                                             anchor='nw',
                                             height=self._get_image_height(),
                                             width=self._get_image_width(),
                                             window=inner_canvas)

            y_pos += self._get_image_height()

    def _get_tk_photos(self):
        if self._tk_images is None:
            self._tk_images = [PIL.ImageTk.PhotoImage(image=ifv.get_image())
                               for ifv in self._images_from_video]
        return self._tk_images

    def _get_window_height(self):
        if self._window_height is None:
            self._window_height = self._root.winfo_screenheight() - 75
        return self._window_height

    def _get_total_images_height(self):
        return self._get_num_images() * self._get_image_height()

    def _get_image_width(self):
        return self._images_from_video[0].get_image().width

    def _get_image_height(self):
        return self._images_from_video[0].get_image().height

    def _get_num_images(self):
        return len(self._images_from_video)

    def run(self):
        self._setup_ui()
        self._root.mainloop()
