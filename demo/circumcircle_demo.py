import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
import tkinter as tk
import geometry_utils as GeometryUtils
import tk_canvas_renderers.canvas_utils as CUtils

def mouse_click(e):
    point = (e.x, e.y)
    Demo().add_point(point)

_root = tk.Tk()
_root.title("Soloshot")

_canvasWidth = 500
_canvasHeight = 500
_label_font = ("arial", 10, "normal")
_canvas = tk.Canvas(_root, width=_canvasWidth, height=_canvasHeight)
_canvas_utils = CUtils.CanvasUtils(_canvas)
_canvas.bind("<Button-1>", mouse_click)
_canvas.pack()    

class _DemoSingleton:
    def __init__(self):
        self.widgets = []
        self.c = (250, 250)
        _canvas_utils.create_dot(self.c, outline="orange", fill="orange")
        self.camera_label = _canvas_utils.create_dot_label(*self.c, "c", fill="orange")
        self.points = []

    def add_point(self, p):
        self.points.append(p)
        self.widgets.append( _canvas_utils.create_dot(p) )
        self.widgets.append( _canvas_utils.create_dot_label(*p, "p" + str(len(self.points))) )
        if len(self.points) > 1:
            self.render_circumcircles(self.points[-2], self.points[-1])
            self.widgets.append( _canvas.create_line(*self.points[-2], *self.points[-1]) )
    
    def render_circumcircles(self, p1, p2):
        theta_rad = GeometryUtils.signed_subtended_angle_from_p1_to_p2_rad(self.c, p1, p2)
        c_centers = GeometryUtils.circumcenters(p1, p2, theta_rad)
        radius = GeometryUtils.circumradius(p1, p2, theta_rad)
        colors = ["orange", "green"]
        for i, c in enumerate(c_centers):
            self.widgets.append( _canvas_utils.create_circle_with_center_and_radius(c, radius, outline=colors[i]) )

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

Demo()
tk.mainloop()