import tkinter as tk
import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')

from tk_canvas_renderers.canvas_utils import CanvasUtils
from viewable_object import RandomlyMovingObject
from boundary import Boundary

def mouse_click(e):
    Demo().add_moving_object()

_root = tk.Tk()
_root.title("Soloshot")

_canvasWidth = 500
_canvasHeight = 500
_label_font = ("arial", 10, "normal")
_canvas = tk.Canvas(_root, width=_canvasWidth, height=_canvasHeight)
_canvas_utils = CanvasUtils(_canvas)
_canvas.bind("<Button-1>", mouse_click)
_canvas.pack()

class _DemoSingleton:
    def __init__(self):
        self.widgets = []
        self.boundary = Boundary([(100, 400), (400,400), (400,100), (100,100)])
        self.boundary_render = _canvas.create_polygon(*self.boundary.exterior.coords, fill='', outline='orange')

    def add_moving_object(self):
        self.moving_object = RandomlyMovingObject(boundary=self.boundary)
        self.widgets.append(_canvas.create_line(*self.moving_object.get_position_history(), fill=CanvasUtils.random_color()))

    def clear(self):
        for w in self.widgets:
            _canvas.delete(w)

        self.widgets = []
        self.points = []


_demo_singleton = None

def Demo():
    global _demo_singleton
    if _demo_singleton == None:
        _demo_singleton = _DemoSingleton()

    return _demo_singleton

_clear_button = tk.Button(_root, text="Clear", command=Demo().clear)
_clear_button.pack()

Demo().add_moving_object()
tk.mainloop()