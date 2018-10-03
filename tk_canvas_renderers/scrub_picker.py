import os
import sys
sys.path.insert(0, os.getcwd())
from tk_canvas_renderers.scrubber import Scrubber # pylint: disable=C0413

class ScrubPicker(Scrubber):

    SELECT_SINGLE_IMAGE = 0
    SELECT_RANGE = 1

    def __init__(self,
                 selector_type=0,
                 **kw):

        self._selector_type = selector_type
        self._selected_start_idx = None
        self._selected_end_idx = None
        self._selected_text = None

        super().__init__(**kw)

    def setup_ui(self):
        super().setup_ui()
        self._selected_text = self._canvas.create_text(50,
                                                       50,
                                                       anchor='w',
                                                       font=Scrubber.SELECT_LABEL_FONT,
                                                      )
        self._canvas.tag_raise(self._selected_text)

    def _button_1_click(self):
        pass

    def _button_2_click(self):
        pass

    def _get_instructions(self):
        if self._selector_type == ScrubPicker.SELECT_SINGLE_IMAGE:
            return "Slide to scrub. Tap to pick frame."

        return "Slide to scrub. Left click to pick begin. Right click to pick end."

    def _left_click(self, _):
        self._selected_start_idx = self._current_photo_idx

        if self._selected_start_idx is self._selected_end_idx:
            self._selected_end_idx = None

        self._display_current_photo()

    def _right_click(self, _):
        if self._selector_type is not ScrubPicker.SELECT_RANGE:
            return

        self._selected_end_idx = self._current_photo_idx

        if self._selected_end_idx is self._selected_start_idx:
            self._selected_start_idx = None

        self._display_current_photo()

    def _update_canvas_overlay(self):
        if self._current_photo_idx is self._selected_start_idx:
            if self._selector_type is ScrubPicker.SELECT_SINGLE_IMAGE:
                self._canvas.itemconfigure(self._selected_text, text='Selected', fill='green')
            else:
                self._canvas.itemconfigure(self._selected_text, text='Start', fill='green')
        elif self._current_photo_idx is self._selected_end_idx:
            self._canvas.itemconfigure(self._selected_text, text='End', fill='red')
        else:
            self._canvas.itemconfigure(self._selected_text, text='')
