import tkinter as tk

class SliderMouseHandler:
    '''
    Used to handle the mouse input to a scrubber. So that when you slide your
    mouse left and right accross a canvas you can detect this movement and scrub
    a video or a track position for example.

    Given a canvas detect x mouse movement on the canvas and calls callback with
    percentage of x position.
    '''

    def __init__(
            self,
            canvas: tk.Canvas,
            margin_pixels: int,
            num_points: int,
            position_idx_callback=None,
            selected_idx_callback=None,
    ):
        self._canvas = canvas
        self._margin_pixels = margin_pixels
        self._num_points = num_points
        self._position_idx_callback = position_idx_callback
        self._selected_idx_callback = selected_idx_callback

        # lazy inits
        self._width = None
        self._right_x = None

        # state
        self._current_idx = 0

        # UI
        self._canvas.bind('<Motion>', self._motion)
        self._canvas.bind('<Button-1>', self._left_click)
        self._canvas.bind('<Button-2>', self._right_click)
        self._canvas.bind('<Enter>', self._enter)
        self._canvas.bind('<Leave>', self._leave)
        self._canvas.bind("<Key>", self._keypress)

    def _motion(self, event):
        self._current_idx = self._get_idx_from_x(self._get_x_from_event(event))
        self._callback_current_idx()

    def _left_click(self, event):
        self._current_idx = self._get_idx_from_x(self._get_x_from_event(event))
        self._callback_selected_current_idx()

    def _right_click(self, event):
        pass

    def _enter(self, _):
        self._canvas.focus_set()

    def _leave(self, event):
        pass

    def _keypress(self, event):
        if event.char == 'j':
            self._step_back()
        elif event.char == 'k':
            self._step_forward()
        elif event.char == 'x':
            self._select_with_x()

    def _step_back(self):
        if self._current_idx > 0:
            self._current_idx = self._current_idx - 1
            self._callback_current_idx()

    def _step_forward(self):
        if self._current_idx < self._num_points - 1:
            self._current_idx = self._current_idx + 1
            self._callback_current_idx()

    def _select_with_x(self):
        self._callback_selected_current_idx()

    def _callback_current_idx(self):
        if self._position_idx_callback is not None:
            self._position_idx_callback(self._current_idx)

    def _callback_selected_current_idx(self):
        if self._selected_idx_callback is not None:
            self._selected_idx_callback(self._current_idx)

    def _get_x_from_event(self, event):
        if event.x > self._get_right_x():
            return self._get_right_x()
        elif event.x < self._margin_pixels:
            return self._margin_pixels
        return event.x

    def _get_percent_from_x(self, x_pos):
        return (x_pos - self._margin_pixels) / (self._get_right_x() - self._margin_pixels)

    def _get_x_from_percent(self, percent):
        return round(percent * self._get_width_of_slider()) + self._margin_pixels

    def _get_idx_from_x(self, x_pos):
        return round(self._get_percent_from_x(x_pos) * (self._num_points - 1))

    def _get_right_x(self):
        if self._right_x is None:
            self._right_x = self._get_width() - self._margin_pixels
        return self._right_x

    def _get_width_of_slider(self):
        return self._get_width() - (2 * self._margin_pixels)

    def _get_width(self):
        if self._width is None:
            self._canvas.update_idletasks()
            self._width = self._canvas.winfo_width()
        return self._width
