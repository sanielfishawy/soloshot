from typing import Iterable
import tkinter as tk
import PIL.ImageTk
import PIL.Image

from tk_canvas_renderers.canvas_utils import CanvasUtils

class VerticalPhotoList:

    def __init__(self, photos: Iterable[PIL.Image.Image],
                 window_height=None,
                 num_photos_displayed_vertically=2):

        self._photos = photos
        self._tk_photos = None
        self._num_photos_displayed_vertically = num_photos_displayed_vertically
        self._window_height = window_height

        self._root = None
        self._outer_frame = None
        self._outer_canvas = None
        self._vbar = None

    def _setup_ui(self):
        self._root = tk.Tk()

        self._outer_frame = tk.Frame(self._root)
        self._outer_frame.grid(row=0, column=0)

        self._outer_canvas = tk.Canvas(self._outer_frame,
                                       scrollregion=(0,
                                                     0,
                                                     self._get_first_photo_resize_width(),
                                                     self._get_total_photo_height()),
                                       background='blue')
        self._outer_canvas.config(width=self._get_first_photo_resize_width(),
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
                                             height=self._get_photo_resize_height(),
                                             width=self._get_first_photo_resize_width(),
                                             window=inner_canvas)

            y_pos += self._get_photo_resize_height()

    def _get_resized_photos(self) -> Iterable[PIL.Image.Image]:
        return [photo.resize(self._get_photo_resize_size())
                for photo in self._photos]

    def _get_tk_photos(self):
        if self._tk_photos is None:
            self._tk_photos = [PIL.ImageTk.PhotoImage(image=photo)
                               for photo in self._get_resized_photos()]
        return self._tk_photos

    def _get_window_height(self):
        if self._window_height is None:
            self._window_height = self._root.winfo_screenheight() - 75
        return self._window_height

    def _get_photo_resize_width(self, photo: PIL.Image.Image):
        return self._get_photo_resize_height() * self._get_aspect_ratio(photo)

    def _get_first_photo_resize_width(self):
        return self._get_photo_resize_width(self._photos[0])

    def _get_photo_resize_height(self):
        return self._get_window_height() / self._num_photos_displayed_vertically

    def _get_photo_resize_size(self):
        return (int(self._get_first_photo_resize_width()), int(self._get_photo_resize_height()))

    def _get_total_photo_height(self):
        return self._get_num_photos() * self._get_photo_resize_height()

    def _get_num_photos(self):
        return len(self._photos)

    def _get_aspect_ratio(self, photo: PIL.Image.Image):
        return photo.width / photo.height

    def run(self):
        self._setup_ui()
        self._root.mainloop()
