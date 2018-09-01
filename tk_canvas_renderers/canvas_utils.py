import random

class CanvasUtils:
    def __init__(self, canvas):
        self.canvas = canvas
        self.label_font = ("arial", 10, "normal")
    
    def create_dot(self, p, **kargs):
        return self.canvas.create_oval(p.x-1, p.y-1, p.x+1, p.y+1, **kargs)

    def create_dot_label(self, x, y, text, **kargs):
        return self.canvas.create_text(x, y+2, text=text, anchor="nw", font=self.label_font, **kargs)

    def create_circle_with_center_and_radius(self, c, r, **kargs):
        return self.canvas.create_oval(c.x-r, c.y-r, c.x+r, c.y+r, **kargs)
    
    @staticmethod
    def random_color():
        return random.choice(CanvasUtils.colors())

    @staticmethod
    def colors():
        return ['blue',
                'red',
                'orange',
                'green',
                'SkyBlue',
                'yellow',
                'DeepPink',
                'chocolate',
                'black',
                'violet']
