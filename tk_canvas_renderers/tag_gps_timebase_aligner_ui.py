# pylint: disable=C0413
import sys
import os
import tkinter as tk
from pathlib import Path

sys.path.insert(0, os.getcwd())
from tk_canvas_renderers.geo_map_scrubber import GeoMapScrubber
from tk_canvas_renderers.scrub_picker import ScrubPicker
from video_and_photo_tools.image_from_video_grabber import ImageFromVideoGrabber

class TagGpsTimebaseAlignerUi:
    '''
    UI used to measure alignment betwen tag_gps timebase and
    video time.
    '''

    def __init__(
            self,
            geo_map_scrubber: GeoMapScrubber,
            video_path: Path,
            save_alignment_callback=None,
            done_callback=None,
    ):
        self._geo_map_scrubber = geo_map_scrubber
        self._geo_map_scrubber.set_selected_callback(self._map_scrubber_selected_callback)

        self._video_path = video_path
        self._save_alignment_callback = save_alignment_callback
        self._done_callback = done_callback

        # Helpers
        self._images_from_video_grabber = ImageFromVideoGrabber(self._video_path)

        # Lazy init
        self._master = None
        self._video_scrub_picker = None

        # State
        self._map_selected_idx = None
        self._map_selected_time = None

    def setup_ui(self, master):
        self._master = master

        control_buttons_frame = tk.Frame(master=master)
        control_buttons_frame.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky=tk.NW,
            padx=10,
            pady=10,
        )

        tk.Button(
            master=control_buttons_frame,
            text='Load Video',
            command=self._load_video_button_click,
            padx=5,
            pady=5,
        ).grid(
            row=0,
            column=0,
            padx=(0, 10),
        )

        tk.Button(
            master=control_buttons_frame,
            text='Save Alignment',
            command=self._save_alignment_button_click,
            padx=5,
            pady=5,
        ).grid(
            row=0,
            column=1,
            padx=(0, 10),
        )

        tk.Button(
            master=control_buttons_frame,
            text='Done',
            command=self._done_button_click,
            padx=5,
            pady=5,
        ).grid(
            row=0,
            column=2,
            padx=(0, 10),
        )

        video_scrub_frame = tk.Frame(master)
        video_scrub_frame.grid(
            row=1,
            column=0,
            sticky=tk.NW,
        )

        self._video_scrub_picker = ScrubPicker(
            images_from_video=self._images_from_video_grabber.get_images_around_frame_number(
                frame_num=0,
                before=0,
                after=100,
            )
        )
        self._video_scrub_picker.setup_ui(master=video_scrub_frame)

        map_scrub_frame = tk.Frame(master)
        map_scrub_frame.grid(
            row=1,
            column=1,
            sticky=tk.NW,
        )
        self._geo_map_scrubber.setup_ui(map_scrub_frame)

    def _load_video_button_click(self):
        assert self._map_selected_idx is not None,\
               'Must select a position on the gps track before loading video'

        images_from_video = self._images_from_video_grabber.get_images_around_time_ms(
            time_ms=self._map_selected_time,
            before=100,
            after=100,
        )
        self._video_scrub_picker.reset_images_from_video(images_from_video)

    def _save_alignment_button_click(self):
        if self._save_alignment_callback is not None:
            ifv = self._video_scrub_picker.get_selected_start_ifv()

            assert ifv is not None, 'Must select a video frame first'
            assert self._map_selected_idx is not None, 'Must select a map track position first'

            self._save_alignment_callback(
                image_from_video=ifv,
                tag_idx=self._map_selected_idx,
                tag_time=self._map_selected_time,
            )

    def _done_button_click(self):
        self._master.destroy()
        if self._done_callback is not None:
            self._done_callback()

    def _map_scrubber_selected_callback(self, idx, time):
        self._map_selected_idx = idx
        self._map_selected_time = time

    def run(self):
        master = tk.Tk()
        self.setup_ui(master)
        master.mainloop()
