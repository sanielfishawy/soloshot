# pylint: disable=W0212, C0413
import sys
import os
import unittest
import tkinter as tk
sys.path.insert(0, os.getcwd())

from tk_canvas_renderers.video_postion_indicator import VideoPositionIndicator


class TestVideoPostionIndicator(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.width = 900
        self.height = 800
        self.margin = 100
        self.canvas = tk.Canvas(master=self.root,
                                width=self.width,
                                height=self.height,
                               )
        self.canvas.grid(column=0, row=0)

        self.indicator = VideoPositionIndicator(self.canvas, self.margin)
        self.root.update_idletasks()
        self.indicator.setup_ui()

    def test_get_left_x(self):
        self.assertEqual(self.indicator._get_left_x(), self.margin)

    def test_get_right_x(self):
        self.assertEqual(self.indicator._get_right_x(), self.width - self.margin + 6)

    def test_winfo_width(self):
        self.assertEqual(self.canvas.winfo_width(), self.width + 6)

    def dont_test_visualize(self):
        self.root.mainloop()



if __name__ == '__main__':
    unittest.main()
