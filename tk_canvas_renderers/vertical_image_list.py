# pylint: disable=C0413
import os
import sys
from typing import List
import tkinter as tk

sys.path.insert(0, os.getcwd())
from tk_canvas_renderers.single_image_canvas import SingleImageCanvas
from video_and_photo_tools.image_from_video import ImageFromVideo


class VerticalImageList:

    IMAGE_FROM_VIDEO = 'image_from_video'
    SELECTED_POINT = 'selected_point'

    def __init__(
            self,
            images_from_video: List[ImageFromVideo],
            window_height=None,
            callback=None,
    ):

        self._images_from_video = images_from_video
        self._window_height = window_height
        self._callback = callback

        self._outer_frame = None
        self._outer_canvas = None
        self._vbar = None
        self._single_image_canvases = None
        self._master = None

    def _setup_ui(self, master):
        self._master = master
        try:
            master.title(self._images_from_video[0].get_video_path().resolve())
        except AttributeError:
            pass


        self._outer_frame = tk.Frame(master)
        self._outer_frame.grid(row=0, column=0)

        self._outer_canvas = tk.Canvas(self._outer_frame,
                                       scrollregion=(0,
                                                     0,
                                                     self._get_image_width(),
                                                     self._get_total_images_height()),
                                       background='blue')
        self._outer_canvas.config(width=self._get_image_width(),
                                  height=self._get_window_height(master))

        self._vbar = tk.Scrollbar(self._outer_frame, orient=tk.VERTICAL)
        self._vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._vbar.config(command=self._outer_canvas.yview)

        self._outer_canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self._outer_canvas.config(yscrollcommand=self._vbar.set)

        self._add_single_image_canvases()

        buttons_frame = tk.Frame(master)
        buttons_frame.grid(
            row=1,
            column=0,
            pady=5,
        )
        done_button = tk.Button(
            master=buttons_frame,
            text='Done',
            command=self._done_click,
            padx=5,
            pady=5,
        )
        done_button.grid(row=0, column=0)

    def _done_click(self):
        if self._callback is not None:
            self._callback(selected_points=self._get_selected_points())
        self._get_root(self._master).destroy()

    def _get_selected_points(self):
        r = []
        for idx, single_image_canvas in enumerate(self._get_single_image_canvases()):
            selected_point = single_image_canvas.get_position_picker().get_selected_point()
            r.append(
                {
                    self.__class__.SELECTED_POINT: selected_point,
                    self.__class__.IMAGE_FROM_VIDEO: self._images_from_video[idx]
                }
            )
        return r

    def _add_single_image_canvases(self):
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

    def _get_window_height(self, widget):
        if self._window_height is None:
            self._window_height = self._get_root(widget).winfo_screenheight() - 95
        return self._window_height

    def _get_root(self, widget):
        root = widget.winfo_toplevel()
        if root.master:
            root = root.master
        return root

    def _get_image_width(self):
        return self._get_first_image().get_image().width

    def _get_image_height(self):
        return self._get_first_image().get_image().height

    def _get_total_images_height(self):
        return self._get_num_images() * self._get_image_height()

    def _get_num_images(self):
        return len(self._images_from_video)

    def _get_first_image(self):
        return self._images_from_video[0]

    def run(self):
        master = tk.Tk()
        self._setup_ui(master)
        master.mainloop()
