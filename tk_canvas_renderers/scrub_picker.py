import os
import sys
sys.path.insert(0, os.getcwd())
from tk_canvas_renderers.scrubber import Scrubber # pylint: disable=C0413

class ScrubPicker(Scrubber):

    SELECT_SINGLE_IMAGE = 0
    SELECT_RANGE = 1
    SELECT_LABEL_FONT = ("arial", 55, "normal")

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
        self._selected_text = self._canvas.create_text(self._get_center_of_canvas_coords()[0],
                                                       self._get_center_of_canvas_coords()[1],
                                                       font=ScrubPicker.SELECT_LABEL_FONT,
                                                      )
        self._canvas.tag_raise(self._selected_text)
        self._set_button_text()

    def _set_button_text(self):
        if self._selector_type == ScrubPicker.SELECT_RANGE:
            self._set_button_1_text('Jump to Start')
            self._set_button_2_text('Jump to End')
        else:
            self._set_button_1_text('Jump to Selected')
            self._button_2.grid_remove()

    def _button_1_click(self):
        # Jump to start
        if self._selected_start_idx is not None:
            self._display_photo(self._selected_start_idx, override_frozen=True)

    def _button_2_click(self):
        # Jump to end
        if self._selected_end_idx is not None:
            self._display_photo(self._selected_end_idx, override_frozen=True)

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

    def _done_click(self):
        if self._callback is not None:
            self._callback([self._get_selected_start_ifv(),
                            self._get_selected_end_ifv(),
                           ]
                          )
        super()._done_click()

    def _get_selected_start_ifv(self):
        if self._selected_start_idx is None:
            return None
        return self._images_from_video[self._selected_start_idx]

    def _get_selected_end_ifv(self):
        if self._selected_end_idx is None:
            return None
        return self._images_from_video[self._selected_end_idx]
