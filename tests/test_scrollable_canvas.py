# pylint: disable=C0413
import sys
import os
import unittest
import tkinter as tk

sys.path.insert(0, os.getcwd())
from tk_canvas_renderers.scrollable_canvas import ScrollableCanvas

class TestScrollableCanvas(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()

    def dont_test_visualize_x_and_y_greater_than_scrollview(self):
        self.create_scrollable_canvas()
        self.root.mainloop()

    def dont_test_visualize_y_greater_than_scrollview(self):
        self.create_scrollable_canvas(
            canvas_width=600,
            canvas_height=1000,
            scrollview_width=700,
            scrollview_height=700,
        )
        self.root.mainloop()

    def dont_test_visualize_x_greater_than_scrollview(self):
        self.create_scrollable_canvas(
            canvas_width=1000,
            canvas_height=600,
            scrollview_width=700,
            scrollview_height=700,
        )
        self.root.mainloop()

    def dont_test_visualize_x_and_y_less_than_scrollview(self):
        self.create_scrollable_canvas(
            canvas_width=600,
            canvas_height=600,
            scrollview_width=700,
            scrollview_height=700,
        )
        self.root.mainloop()

    def create_scrollable_canvas(
            self,
            canvas_width=1000,
            canvas_height=1000,
            scrollview_width=700,
            scrollview_height=700,
    ):
        scrollable_canvas = ScrollableCanvas(
            self.root,
            canvas_width,
            canvas_height,
            scrollview_width,
            scrollview_height,
        ).get_canvas()

        scrollable_canvas.create_rectangle(0, 0, 100, 100, fill='red')


if __name__ == '__main__':
    unittest.main()
