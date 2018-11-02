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
            position_percent_callback=None,
            selected_percent_callback=None,
    ):
        self._canvas = canvas
        self._margin_pixels = margin_pixels
        self._position_percent_callback = position_percent_callback
        self._selected_percent_callback = selected_percent_callback

        # lazy inits
        self._width = None
        self._right_x = None

        # UI
        self._canvas.bind('<Motion>', self._motion)
        self._canvas.bind('<Button-1>', self._left_click)
        self._canvas.bind('<Button-2>', self._right_click)
        self._canvas.bind('<Enter>', self._enter)
        self._canvas.bind('<Leave>', self._leave)

    def _motion(self, event):
        if self._position_percent_callback is not None:
            self._position_percent_callback(self._get_percent_from_x(self._get_x_from_event(event)))

    def _left_click(self, event):
        if self._selected_percent_callback is not None:
            self._selected_percent_callback(self._get_percent_from_x(self._get_x_from_event(event)))

    def _right_click(self):
        pass

    def _enter(self, event):
        pass

    def _leave(self, event):
        pass

    def _get_x_from_event(self, event):
        if event.x > self._get_right_x():
            return self._get_right_x()
        elif event.x < self._margin_pixels:
            return self._margin_pixels
        return event.x

    def _get_percent_from_x(self, x_pos):
        return (x_pos - self._margin_pixels) / (self._get_right_x() - self._margin_pixels)

    def _get_right_x(self):
        if self._right_x is None:
            self._right_x = self._get_width() - self._margin_pixels
        return self._right_x

    def _get_width(self):
        if self._width is None:
            self._canvas.update_idletasks()
            self._width = self._canvas.winfo_width()
        return self._width
