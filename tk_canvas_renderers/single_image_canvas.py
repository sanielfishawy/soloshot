# pylint: disable=C0413
import os
import sys
import tkinter as tk
import PIL.ImageTk
sys.path.insert(0, os.getcwd())
from video_and_photo_tools.image_from_video import ImageFromVideo
from tk_canvas_renderers.canvas_utils import CanvasUtils
from tk_canvas_renderers.canvas_position_picker import CanvasPositionPicker

class SingleImageCanvas:

    def __init__(self,
                 master,
                 image_from_video: ImageFromVideo,
                ):

        self._master = master
        self._image_from_video = image_from_video

        self._canvas = None
        self._tk_photo = None
        self._position_picker = None

        self._info_color = 'blue'
        self._info_font = ('Helvetica', '12')
        self._setup_ui()

    def _setup_ui(self):
        self._canvas = tk.Canvas(master=self._master,
                                 bg=CanvasUtils.random_color(),
                                )
        self._canvas.create_image(0,
                                  0,
                                  image=self._get_tk_photo(),
                                  anchor='nw')

        frame_num = self._canvas.create_text(10,
                                             20,
                                             text=f'Frame: {self._image_from_video.get_formatted_frame_num()}', # pylint: disable=C0301
                                             fill=self._info_color,
                                             anchor=tk.W,
                                             font=self._info_font,
                                            )
        self._canvas.tag_raise(frame_num)

        frame_ms = self._canvas.create_text(10,
                                            40,
                                            text=f'Time: {self._image_from_video.get_formatted_time_ms()} ms', # pylint: disable=C0301
                                            fill=self._info_color,
                                            anchor=tk.W,
                                            font=self._info_font,
                                            )
        self._canvas.tag_raise(frame_ms)
        self._master.update_idletasks()
        self._position_picker = CanvasPositionPicker(self._canvas,
                                                     self.get_width(),
                                                     self.get_height(),
                                                    )
        return self

    def get_width(self):
        return self._image_from_video.get_image().width

    def get_height(self):
        return self._image_from_video.get_image().height

    def get_canvas(self):
        return self._canvas

    def _get_tk_photo(self):
        if self._tk_photo is None:
            self._tk_photo = PIL.ImageTk.PhotoImage(image=self._image_from_video.get_image())
        return self._tk_photo
