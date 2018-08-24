import tkinter as tk
import geometry_utils as GeometryUtils

def mouse_click(e):
    Test().clear()
    Test().test((e.x, e.y))

_root = tk.Tk()
_root.title("Soloshot")

_canvasWidth = 500
_canvasHeight = 500
_label_font = ("arial", 10, "normal")
_canvas = tk.Canvas(_root, width=_canvasWidth, height=_canvasHeight)
_canvas.bind("<Button-1>", mouse_click)
_canvas.pack()    

class _TestSingleton:
    def __init__(self):
        self.widgets = []
        self.p1 = (250, 250)
        _canvas.create_text((250, 250), text="p1") 


    def test(self, p2, theta_deg=70):
        (r1, r2) = GeometryUtils.isosceles_points(self.p1, p2, theta_deg) 
        
        self.widgets.append( _canvas.create_text(p2, text="p2") )
        self.widgets.append( _canvas.create_line(self.p1, p2, fill="blue") )
        self.widgets.append( _canvas.create_line(r1, r2, fill="red") )
        self.widgets.append( _canvas.create_text(r1, text="r1") )
        self.widgets.append( _canvas.create_text(r2, text="r2") )
    
    def clear(self):
        for w in self.widgets:
            _canvas.delete(w)
        
        self.widgets = []


_test_singleton = None

def Test():
    global _test_singleton
    if _test_singleton == None:
        _test_singleton = _TestSingleton()
    
    return _test_singleton


tk.mainloop()