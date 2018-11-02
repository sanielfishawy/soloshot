import sys
import os
import abc
from typing import List
import tkinter as tk
import PIL.Image
import PIL.ImageTk

sys.path.insert(0, os.getcwd())
from video_and_photo_tools.image_from_video import ImageFromVideo # pylint: disable=C0413
from tk_canvas_renderers.video_postion_indicator import VideoPositionIndicator # pylint: disable=C0413

class Scrubber:

    def __init__(self,
                 images_from_video: List[ImageFromVideo] = None,
                 callback=None,
                ):
        '''
        :param photos Iterable[ImageFromVideo]: pics have equal dims typically extracted using VideoHelper
        '''
        assert (images_from_video is not None), 'images_from_video_parameter must be provided'
        self._images_from_video = images_from_video
        self._callback = callback

        # Constants
        self._margin_for_cursor_scrub = .2

        # State
        self._current_photo_idx = 0
        self._is_frozen = False

        # Lazy init
        self._master = None
        self._tk_photos = None
        self._instructions_label = None
        self._frame_num_label = None
        self._frame_ms_label = None
        self._canvas = None
        self._canvas_utils = None
        self._photo_on_canvas = None
        self._done_button = None
        self._button_1 = None
        self._button_2 = None
        self._video_position_indicator = None

    @abc.abstractmethod
    def setup_ui(self, master=None):
        assert master is not None, 'Must set master in setup_ui'

        self._master = master
        if 'title' in dir(master):
            master.title(str(self._get_video_path().resolve()))

        self._instructions_label = tk.Label(master=master,
                                            text=self._get_instructions(),
                                           )
        self._instructions_label.grid(row=0, column=0, columnspan=3, pady=10)

        self._frame_num_label = tk.Label(master=master,
                                         text=self._get_frame_num_label_text(),
                                        )
        self._frame_num_label.grid(row=1, column=0, sticky=tk.W, padx=10)

        self._frame_ms_label = tk.Label(master=master,
                                        text=self._get_frame_ms_label_text(),
                                       )
        self._frame_ms_label.grid(row=2, column=0, sticky=tk.W, padx=10)

        self._canvas = tk.Canvas(master=master,
                                 width=self._get_photos_width(),
                                 height=self._get_photos_height(),
                                )
        self._canvas.bind('<Motion>', self._motion)
        self._canvas.bind('<Button-1>', self._left_click)
        self._canvas.bind('<Button-2>', self._right_click)
        self._canvas.bind('<Enter>', self._enter)
        self._canvas.bind('<Leave>', self._leave)
        self._canvas.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
        self._photo_on_canvas = self._canvas.create_image(0, 0, anchor='nw')

        self._video_position_indicator = VideoPositionIndicator(self._canvas,
                                                                self._get_left_scrub_bound()) # pylint: disable=C0301
        self._video_position_indicator.setup_ui()

        self._done_button = tk.Button(master=master,
                                      text="Done",
                                      command=self._done_click,
                                      padx=5,
                                      pady=5,
                                     )
        self._done_button.grid(row=4, column=2, pady=(0, 10))

        self._button_1 = tk.Button(master=master,
                                   text="Button 1",
                                   command=self._button_1_click,
                                   padx=5,
                                   pady=5,
                                  )
        self._button_1.grid(row=4, column=0, pady=(0, 10))

        self._button_2 = tk.Button(master=master,
                                   text="Button 2",
                                   command=self._button_2_click,
                                   padx=5,
                                   pady=5,
                                  )
        self._button_2.grid(row=4, column=1, pady=(0, 10))

        self._display_current_photo()

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

    def _get_frame_num_label_text(self):
        return 'Frame: ' + '{:,}'.format(self._get_current_image_from_video().get_frame_num())

    def _get_frame_ms_label_text(self):
        return 'Time: ' + '{:,}'.format(self._get_current_image_from_video().get_time_ms()) + 'ms'

    def _get_center_of_canvas_coords(self):
        return (int(self._get_photos_width() / 2), int(self._get_photos_height() / 2))

    def _set_button_1_text(self, text):
        self._button_1.config(text=text)

    def _set_button_2_text(self, text):
        self._button_2.config(text=text)

    def _get_video_path(self):
        return self._images_from_video[0].get_video_path()

    def _get_photos_width(self):
        return self._images_from_video[0].get_image().width

    def _get_photos_height(self):
        return self._images_from_video[0].get_image().height

    def _motion(self, event):
        self._display_photo(self._get_idx_from_cursor_x(event.x))

    def _get_left_scrub_bound(self):
        return self._margin_for_cursor_scrub * self._get_photos_width()

    def _get_right_scrub_bound(self):
        return (1 - self._margin_for_cursor_scrub) * self._get_photos_width()

    def _get_idx_from_cursor_x(self, cursor_x):
        width_of_scrub = self._get_right_scrub_bound() - self._get_left_scrub_bound()
        if cursor_x <= self._get_left_scrub_bound():
            return 0

        idx = int(self._get_num_images_from_video() * (cursor_x - self._get_left_scrub_bound()) / width_of_scrub) # pylint: disable=C0301
        return min(idx, self._get_num_images_from_video() - 1)

    def _get_tk_photos(self):
        if self._tk_photos is None:
            self._tk_photos = [PIL.ImageTk.PhotoImage(image=ifv.get_image())
                               for ifv in self._images_from_video]
        return self._tk_photos

    def _get_current_image_from_video(self):
        return self._images_from_video[self._current_photo_idx]

    def _display_current_photo(self):
        self._display_photo(self._current_photo_idx)
        return self

    def _display_photo(self, idx, override_frozen=False):
        if self._handle_frozen(idx) or override_frozen:
            self._current_photo_idx = idx
            self._canvas.itemconfig(self._photo_on_canvas, image=self._get_tk_photos()[idx])
            self._update_canvas_overlay()
            self._update_video_position_indicator()
            self._update_frame_num_and_ms_text()
            self._master.update()
        return self

    def _handle_frozen(self, idx):
        if self._is_frozen:
            if self._current_photo_idx == idx:
                self._un_freeze()
                return True
            else:
                return False
        return True

    def _update_frame_num_and_ms_text(self):
        self._frame_num_label.config(text=self._get_frame_num_label_text())
        self._frame_ms_label.config(text=self._get_frame_ms_label_text())

    def _update_video_position_indicator(self):
        percent = self._current_photo_idx / self._get_num_images_from_video()
        self._video_position_indicator.set_percent(percent)
        return self

    def _done_click(self):
        if 'destroy' in dir(self._master):
            self._master.destroy()

    def _leave(self, _):
        self._freeze()

    def _enter(self, event):
        pass

    def _freeze(self):
        self._is_frozen = True

    def _un_freeze(self):
        self._is_frozen = False

    def _get_num_images_from_video(self):
        return len(self._images_from_video)

    def run(self):
        master = tk.Tk()
        self.setup_ui(master)
        master.mainloop()
        return self
