import sys
import os
from typing import List
from pathlib import Path
import tkinter as tk
import PIL.Image
import PIL.ImageTk

sys.path.insert(0, os.getcwd())
from video_and_photo_tools.image_from_video import ImageFromVideo

class StillPicker:

    def __init__(self, images_from_video: List[ImageFromVideo], width=600):
        '''
        :param photos Iterable[ImageFromVideo]: pics have equal dimensions typically extracted using VideoHelper
        '''
        self._images_from_video = images_from_video
        self._width = width
        self._margin_for_cursor_scrub = .16

        self._current_photo_idx = 0
        self._tk_photos = None

        self._root = None
        self._canvas = None
        self._photo_on_canvas = None
        self._next_button = None

    def setup_ui(self):
        self._root = tk.Tk()

        self._canvas = tk.Canvas(master=self._root,
                                 width=self._width,
                                 height=self._get_resize_height(),
                                #  bg='blue',
                                )
        self._canvas.bind('<Motion>', self._motion)
        self._canvas.grid(row=0, column=0)
        self._photo_on_canvas = self._canvas.create_image(0, 0, anchor='nw')
        self._next_button = tk.Button(master=self._root, text="Next", command=self._next_click)
        self._next_button.grid(row=1, column=0)

        self._display_current_photo()
        return self

    def _motion(self, event):
        self._display_photo(self._get_idx_from_cursor_x(event.x))

    def _get_idx_from_cursor_x(self, cursor_x):
        left_scrub_bound = self._margin_for_cursor_scrub * self._width
        right_scrub_bound = (1 - self._margin_for_cursor_scrub) * self._width
        width_of_scrub = right_scrub_bound - left_scrub_bound

        if cursor_x < left_scrub_bound:
            return 0

        if cursor_x > right_scrub_bound:
            return self._get_num_images_from_video() - 1

        return int(self._get_num_images_from_video() * (cursor_x - left_scrub_bound) / width_of_scrub)

    def _get_aspect_ratio(self):
        img = self._images_from_video[0].get_image()
        return img.width / img.height

    def _get_resize_height(self):
        return int(self._width / self._get_aspect_ratio())

    def _get_resize_size(self):
        return (self._width, self._get_resize_height())

    def _get_tk_photos(self):
        if self._tk_photos is None:
            self._tk_photos = [PIL.ImageTk.PhotoImage(image=photo)
                               for photo in self._get_resized_photos()]
        return self._tk_photos

    def _get_resized_photos(self):
        return [ifv.get_image().resize(self._get_resize_size(),
                                       PIL.Image.ANTIALIAS) for ifv in self._images_from_video]

    def _display_current_photo(self):
        self._display_photo(self._current_photo_idx)
        return self

    def _display_photo(self, idx):
        self._canvas.itemconfig(self._photo_on_canvas, image=self._get_tk_photos()[idx])
        self._root.update()
        return self

    def _display_next_photo(self):
        self._increment_photo_idx()
        self._display_current_photo()

    def _increment_photo_idx(self):
        self._current_photo_idx = (self._current_photo_idx + 1) % len(self._images_from_video)
        return self

    def _next_click(self):
        for _ in range(1000):
            self._display_next_photo()
        return self

    def _get_num_images_from_video(self):
        return len(self._images_from_video)

    def run(self):
        self.setup_ui()
        self._root.mainloop()
        return self