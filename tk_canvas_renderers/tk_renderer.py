import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
import tkinter as tk
from shapely.geometry import Point

class _TKRenderer:

    def __init__(self, scale=1, canvas_width=500, canvas_height=500, font_size=10):
        self.root = tk.Tk()
        self.root.title("Soloshot")

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.label_font = ("arial", font_size, "normal")
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height)
        # self.canvas.bind("<Button-1>", mouse_click)
        self.scale = scale
        self.canvas.pack()    

    def get_canvas(self):
        return self.canvas

    def get_scale(self):
        return self.scale

    def set_scale(self, scale):
        self.scale = scale
        return scale

    def start_tk_event_loop(self):
        tk.mainloop()
        return self

    def scale_tuple(self, tpl):
        return tuple([ t * self.scale for t in tpl ])

    def scale_coords(self, crds):
        return list(map(self.scale_tuple, crds))

    def delete_elements(self, elements):
        for el in elements:
            self.canvas.delete(el)
        return self

    # Render geometries with scale
    def create_polygon(self, crds, **kargs):
        return self.canvas.create_polygon(*self.scale_coords(crds), **kargs)

    def create_dot(self, crds, **kargs):
        s_crds = self.scale_tuple(crds)
        return self.canvas.create_oval(s_crds[0]-1, s_crds[1]-1, s_crds[0]+1, s_crds[1]+1, **kargs)

    def create_dot_label(self, crds, text, **kargs):
        s_crds = self.scale_tuple(crds)
        return self.canvas.create_text(s_crds[0]+6, s_crds[1]-1, text=text, anchor="se", font=self.label_font, **kargs)

    def create_circle_with_center_and_radius(self, c, r, **kargs):
        return self.canvas.create_oval(c.x-r, c.y-r, c.x+r, c.y+r, **kargs)
_tk_renderer = None

def TKRenderer(**kargs):
    global _tk_renderer
    if _tk_renderer == None:
        _tk_renderer = _TKRenderer(**kargs)

    return _tk_renderer