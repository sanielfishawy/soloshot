# pylint: disable=C0413
import sys
import os
import tkinter as tk

sys.path.insert(0, os.getcwd())
from tk_canvas_renderers.geo_map_scrubber import GeoMapScrubber
from tk_canvas_renderers.scrub_picker import ScrubPicker

class VideoPlusMapScrubPicker:
    '''
    A tkinter layout including video ScrubPicker and GeoMapScrubber
    '''

    def __init__(
            self,
            video_scrub_picker: ScrubPicker,
            geo_map_scrubber: GeoMapScrubber,
    ):
        self._video_scrub_picker = video_scrub_picker
        self._geo_map_scrubber = geo_map_scrubber

        # Lazy init
        self._video_scrub_frame = None
        self._geo_map_scrub_frame = None


    def setup_ui(self, master):
        self._video_scrub_frame = tk.Frame(master)

        self._video_scrub_picker.setup_ui(
            master=self._video_scrub_frame,
        )

        self._video_scrub_frame.grid(
            column=0,
            row=0,
            sticky=tk.N+tk.E,
        )

        self._geo_map_scrub_frame = tk.Frame(master)
        self._geo_map_scrubber.setup_ui(self._geo_map_scrub_frame)
        self._geo_map_scrub_frame.grid(
            column=1,
            row=0,
            sticky=tk.N+tk.E,
        )


    def run(self):
        master = tk.Tk()
        self.setup_ui(master)
        master.mainloop()
