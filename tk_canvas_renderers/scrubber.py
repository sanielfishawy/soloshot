import sys
import os
import abc
from typing import List
import tkinter as tk
import PIL.Image
import PIL.ImageTk

sys.path.insert(0, os.getcwd())
from video_and_photo_tools.image_from_video import ImageFromVideo # pylint: disable=C0413

class Scrubber:

    def __init__(self,
                 images_from_video: List[ImageFromVideo] = None,
                 callback=None,
                ):
        '''
        :param photos Iterable[ImageFromVideo]: pics have equal dimensions typically extracted using VideoHelper
        '''
        assert (images_from_video is not None), 'images_from_video_parameter must be provided'
        self._images_from_video = images_from_video

        self._margin_for_cursor_scrub = .2
        self._callback = callback

        self._current_photo_idx = 0
        self._tk_photos = None

        self._root = None
        self._canvas = None
        self._photo_on_canvas = None
        self._done_button = None
        self._button_1 = None
        self._button_2 = None

    @abc.abstractmethod
    def setup_ui(self):
        self._root = tk.Tk()

        instructions_label = tk.Label(master=self._root,
                                      text=self._get_instructions(),
                                     )
        instructions_label.grid(row=0, column=0, columnspan=3, pady=(10))

        self._canvas = tk.Canvas(master=self._root,
                                 width=self._get_photos_width(),
                                 height=self._get_photos_height(),
                                )
        self._canvas.bind('<Motion>', self._motion)
        self._canvas.bind('<Button-1>', self._left_click)
        self._canvas.bind('<Button-2>', self._right_click)
        self._canvas.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        self._photo_on_canvas = self._canvas.create_image(0, 0, anchor='nw')

        self._done_button = tk.Button(master=self._root,
                                      text="Done",
                                      command=self._done_click,
                                      padx=5,
                                      pady=5,
                                     )
        self._done_button.grid(row=2, column=2, pady=(0, 10))

        self._button_1 = tk.Button(master=self._root,
                                   text="Button 1",
                                   command=self._button_1_click,
                                   padx=5,
                                   pady=5,
                                  )
        self._button_1.grid(row=2, column=0, pady=(0, 10))

        self._button_2 = tk.Button(master=self._root,
                                   text="Button 2",
                                   command=self._button_2_click,
                                   padx=5,
                                   pady=5,
                                  )
        self._button_2.grid(row=2, column=1, pady=(0, 10))

        self._display_current_photo()
        return self

    @abc.abstractmethod
    def _get_instructions(self):
        return 'Scrubber instructions'

    @abc.abstractmethod
    def _left_click(self, _):
        pass

    @abc.abstractmethod
    def _right_click(self, _):
        pass

    @abc.abstractmethod
    def _update_canvas_overlay(self):
        pass

    @abc.abstractmethod
    def _button_1_click(self):
        pass

    @abc.abstractmethod
    def _button_2_click(self):
        pass

    def _get_center_of_canvas_coords(self):
        return (int(self._get_photos_width() / 2), int(self._get_photos_height() / 2))

    def _set_button_1_text(self, text):
        self._button_1.config(text=text)

    def _set_button_2_text(self, text):
        self._button_2.config(text=text)

    def _get_photos_width(self):
        return self._images_from_video[0].get_image().width

    def _get_photos_height(self):
        return self._images_from_video[0].get_image().height

    def _motion(self, event):
        self._display_photo(self._get_idx_from_cursor_x(event.x))

    def _get_idx_from_cursor_x(self, cursor_x):
        left_scrub_bound = self._margin_for_cursor_scrub * self._get_photos_width()
        right_scrub_bound = (1 - self._margin_for_cursor_scrub) * self._get_photos_width()
        width_of_scrub = right_scrub_bound - left_scrub_bound

        if cursor_x <= left_scrub_bound:
            return 0

        idx = int(self._get_num_images_from_video() * (cursor_x - left_scrub_bound) / width_of_scrub) # pylint: disable=C0301
        return min(idx, self._get_num_images_from_video() - 1)

    def _get_tk_photos(self):
        if self._tk_photos is None:
            self._tk_photos = [PIL.ImageTk.PhotoImage(image=ifv.get_image())
                               for ifv in self._images_from_video]
        return self._tk_photos

    def _display_current_photo(self):
        self._display_photo(self._current_photo_idx)
        return self

    def _display_photo(self, idx):
        self._current_photo_idx = idx
        self._canvas.itemconfig(self._photo_on_canvas, image=self._get_tk_photos()[idx])
        self._update_canvas_overlay()
        self._root.update()
        return self

    def _done_click(self):
        self._root.destroy()

    def _get_num_images_from_video(self):
        return len(self._images_from_video)

    def run(self):
        self.setup_ui()
        self._root.mainloop()
        return self
