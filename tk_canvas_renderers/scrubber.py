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

    SELECT_SINGLE_IMAGE = 0
    SELECT_RANGE = 1
    SELECT_LABEL_FONT = ("arial", 35, "normal")

    def __init__(self,
                 images_from_video: List[ImageFromVideo],
                 selector_type=0,
                 callback=None,
                ):
        '''
        :param photos Iterable[ImageFromVideo]: pics have equal dimensions typically extracted using VideoHelper
        '''
        self._images_from_video = images_from_video
        self._margin_for_cursor_scrub = .2
        self._selector_type = selector_type
        self._callback = callback

        self._current_photo_idx = 0
        self._selected_start_idx = None
        self._selected_end_idx = None
        self._tk_photos = None

        self._root = None
        self._canvas = None
        self._photo_on_canvas = None
        self._done_button = None
        self._button_1 = None
        self._button_2 = None
        self._selected_text = None

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
        self._selected_text = self._canvas.create_text(50,
                                                       50,
                                                       anchor='w',
                                                       font=Scrubber.SELECT_LABEL_FONT,
                                                      )
        self._canvas.tag_raise(self._selected_text)

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

    def _get_photos_width(self):
        return self._images_from_video[0].get_image().width

    def _get_photos_height(self):
        return self._images_from_video[0].get_image().height

    def _get_instructions(self):
        if self._selector_type == Scrubber.SELECT_SINGLE_IMAGE:
            return "Slide to scrub. Tap to pick frame."

        return "Slide to scrub. Left click to pick begin. Right click to pick end."

    def _motion(self, event):
        self._display_photo(self._get_idx_from_cursor_x(event.x))

    def _left_click(self, _):
        self._selected_start_idx = self._current_photo_idx

        if self._selected_start_idx is self._selected_end_idx:
            self._selected_end_idx = None

        self._display_current_photo()

    def _right_click(self, _):
        if self._selector_type is not Scrubber.SELECT_RANGE:
            return

        self._selected_end_idx = self._current_photo_idx

        if self._selected_end_idx is self._selected_start_idx:
            self._selected_start_idx = None

        self._display_current_photo()

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
        self._update_selected_text()
        self._root.update()
        return self

    def _update_selected_text(self):
        if self._current_photo_idx is self._selected_start_idx:
            if self._selector_type is Scrubber.SELECT_SINGLE_IMAGE:
                self._canvas.itemconfigure(self._selected_text, text='Selected', fill='green')
            else:
                self._canvas.itemconfigure(self._selected_text, text='Start', fill='green')
        elif self._current_photo_idx is self._selected_end_idx:
            self._canvas.itemconfigure(self._selected_text, text='End', fill='red')
        else:
            self._canvas.itemconfigure(self._selected_text, text='')

    def _done_click(self):
        self._root.destroy()

    @abc.abstractmethod
    def _button_1_click(self):
        pass

    @abc.abstractmethod
    def _button_2_click(self):
        pass

    def _get_num_images_from_video(self):
        return len(self._images_from_video)

    def run(self):
        self.setup_ui()
        self._root.mainloop()
        return self
