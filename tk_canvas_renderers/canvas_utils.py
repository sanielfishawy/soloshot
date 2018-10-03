import random

class CanvasUtils:
    def __init__(self, canvas):
        self.canvas = canvas
        self.label_font = ("arial", 10, "normal")

    def create_dot(self, p, radius=1, **kargs):
        return self.canvas.create_oval(p[0]-radius, p[1]-radius, p[0]+radius, p[1]+radius, **kargs)

    def create_dot_label(self, x, y, text, **kargs):
        return self.canvas.create_text(x,
                                       y+2,
                                       text=text,
                                       anchor="nw",
                                       font=self.label_font, **kargs)

    def create_circle_with_center_and_radius(self, c, r, **kargs):
        return self.canvas.create_oval(c[0]-r, c[1]-r, c[0]+r, c[1]+r, **kargs)

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
