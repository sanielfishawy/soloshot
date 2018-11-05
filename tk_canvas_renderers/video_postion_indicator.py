import sys
import os
import tkinter as tk
sys.path.insert(0, os.getcwd())

class VideoPositionIndicator:
    '''Widget that is a line with a dot which slides back and forth along the line
       used to indicate where in a scrub the current position is'''

    def __init__(self,
                 canvas: tk.Canvas,
                 left_right_margin,
                ):

        self._canvas = canvas
        self._canvas.config(highlightcolor='white')
        self._canvas.update_idletasks() # To update dimensions in winfo calls.

        self._left_right_margin = left_right_margin

        # Lazy init
        self._line = None
        self._dot = None
        self._selected_circle = None
        self._percent = 0

        # Constants
        self._dot_radius = 4
        self._color = 'red'
        self._selected_circle_color = 'blue'
        self._selected_circle_width = 3
        self._selected_circle_radius = 6
        self._line_width = 3
        self._bottom_margin = 20


    def setup_ui(self):

        self._line = self._canvas.create_line(self._get_left_x(),
                                              self._get_y(),
                                              self._get_right_x(),
                                              self._get_y(),
                                              width=self._line_width,
                                              fill=self._color
                                             )
        self._canvas.tag_raise(self._line)

        self._dot = self._canvas.create_oval(
            self._get_oval_coords(
                self._get_x_pos_with_percent(self._percent),
                self._dot_radius,
            ),
            fill=self._color,
            outline=self._color,
        )
        self._canvas.tag_raise(self._dot)
        return self

    def set_percent(self, percent):
        self._percent = percent
        self._canvas.coords(
            self._dot,
            self._get_oval_coords(
                self._get_x_pos_with_percent(percent),
                self._dot_radius,
            ),
        )
        return self

    def set_selected(self, percent):
        if self._selected_circle is not None:
            self._canvas.delete(self._selected_circle)
        self._selected_circle = self._canvas.create_oval(
            self._get_oval_coords(
                self._get_x_pos_with_percent(percent),
                self._selected_circle_radius,
            ),
            outline=self._selected_circle_color,
            width=self._selected_circle_width,
        )

    def _get_x_pos_with_percent(self, percent):
        return self._get_left_x() + int(percent * self._get_x_width())

    def _get_left_x(self):
        return self._left_right_margin

    def _get_right_x(self):
        return self._canvas.winfo_width() - self._left_right_margin

    def _get_x_width(self):
        return self._get_right_x() - self._get_left_x()

    def _get_y(self):
        return self._canvas.winfo_height() - self._bottom_margin

    def _get_oval_coords(self, x_pos, radius):
        return [
            x_pos - radius,
            self._get_y() - radius,
            x_pos + radius,
            self._get_y() + radius,
        ]
