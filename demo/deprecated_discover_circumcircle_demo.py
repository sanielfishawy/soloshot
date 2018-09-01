import tkinter as tk
import math as math
import time as time
import tk_canvas_renderers.canvas_utils as CUtils


def mouse_click(e):
    if Camera() == None:
        Camera(e.x, e.y)   
    else:
        Tags().add_tag(e.x, e.y)
    
    if  Tags().get_num_tags() > 1:
        last_two_tags = [Tags().get_tags()[-2], Tags().get_tags()[-1]]
        # possible_camera_positions = CameraPositionCalculator(last_two_tags).calc()
        # CameraPositionRender(possible_camera_positions).render()



_root = tk.Tk()
_root.title("Soloshot")

_canvasWidth = 500
_canvasHeight = 500
_label_font = ("arial", 10, "normal")
_canvas = tk.Canvas(_root, width=_canvasWidth, height=_canvasHeight)
_canvas_utils = CUtils.CanvasUtils(_canvas)
_canvas.bind("<Button-1>", mouse_click)
_canvas.pack()

class _CameraSingleton:
    def __init__(self, x, y):
        self.camera_color = "red"
        self.x = x
        self.y = y
        self.render_camera()

    def get_position(self):
        return (self.x, self.y)

    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y

    def camera_label(self):
        return "C (" + str(self.x) + ", " + str(self.y) + ")"
    
    def render_camera(self):
        #self.dot = _canvas_utils.add_dot(self.x, self.y, color = self.camera_color)
        self.label = _canvas_utils.create_dot_label(self.x, self.y, self.camera_label(), color=self.camera_color)

_camera_singleton = None

def Camera(x=None,y=None):
    global _camera_singleton

    if x == None or y == None:
        return _camera_singleton

    if _camera_singleton == None:
        _camera_singleton = _CameraSingleton(x, y)

    return _camera_singleton

class Tag:
    def __init__(self, x, y, n):
        self.tag_color = "blue"
        self.x = x
        self.y = y
        self.n = n
        self.render_tag()
        self.render_line_to_camera()

    def get_position(self):
        return (self.x, self.y)

    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def get_n(self):
        return self.n
        
    def str_position(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"
    
    def tag_label(self): 
        return "T" + str(self.n) # + self.str_position() 
        
    def render_tag(self): 
        #self.dot = _canvas_utils.add_dot(self.x, self.y, color=self.tag_color) 
        self.label = _canvas_utils.create_dot_label(self.x, self.y, self.tag_label(), color=self.tag_color, anchor="sw") 

    def render_line_to_camera(self):
        self.line_to_camera = _canvas.create_line(self.x, self.y, Camera().get_x(), Camera().get_y(), fill=self.tag_color)

    def vector_from_camera(self):
        return [Camera().get_x(), Camera().get_y(), self.x, self.y]


class LineBetweenTags:
    def __init__(self, tags):
        self.color = "green"
        self.tags = tags
    
    def render(self):
        self.render_line()
        self.render_label()

    def render_line(self):
        self.line = _canvas.create_line(self.tags[0].get_x(), self.tags[0].get_y(), 
                                        self.tags[1].get_x(), self.tags[1].get_y(), 
                                        fill=self.color)

    def render_label(self):
        pos = VectorUtils.midpoint(self.get_vector())
        self.label = _canvas.create_text( pos[0], pos[1], text=self.label_text(), 
                                          angle=VectorUtils.angle(self.get_vector()),
                                          font=_label_font, fill=self.color, anchor="s")
    
    def label_text(self):
        return "A" + str(self.tags[0].get_n()) + " (" + str(VectorUtils.int_magnitude(self.get_vector())) + ")"
        
    def get_vector(self):
        return [ self.tags[0].get_x(), self.tags[0].get_y(), self.tags[1].get_x(), self.tags[1].get_y() ]
    
    def get_magnitude(self):
        return VectorUtils.magnitude(self.get_vector())
    
    def get_int_magnitude(self):
        return VectorUtils.int_magnitude(self.get_vector())

class AngleBetweenTags:
    def __init__(self, tags):
        self.color = "green"
        self.arc_radius = 15
        self.tags = tags
        self.start_extent_mid = self._start_extent_mid()
    
    def get_angle(self):
        return abs(self.start_extent_mid[1])

    def render(self):
        self.render_angle()
        self.render_label()
        
    def arc_box(self):
        return [Camera().get_x() - self.arc_radius,
                Camera().get_y() - self.arc_radius,
                Camera().get_x() + self.arc_radius,
                Camera().get_y() + self.arc_radius]

    def _start_extent_mid(self):
        start = VectorUtils.angle360(self.tags[0].vector_from_camera())
        extent = VectorUtils.angle360(self.tags[1].vector_from_camera()) - start

        if extent > 180:
            extent = extent - 360

        mid = start + extent / 2
        
        return (start, extent, mid)

    def render_angle(self):
        (start, extent, mid) = self.start_extent_mid

        mid #not used

        self.arc = _canvas.create_arc(self.arc_box()[0],
                                      self.arc_box()[1], 
                                      self.arc_box()[2], 
                                      self.arc_box()[3],
                                      start=start, 
                                      extent=extent,
                                      style=tk.ARC,
                                      outline=self.color) 
    
    def render_label(self):
        (start, extent, mid) = self.start_extent_mid

        start #not used

        vector = VectorUtils.vector_with_angle_and_magnitude(Camera().get_position(), mid, 20)
        label_position = VectorUtils.tip(vector)
        text = "a" + str(self.tags[0].get_n()) + " (" + str(int(abs(extent))) + ")"

        self.label = _canvas.create_text(label_position[0], label_position[1],
                                         text=text, angle=mid, anchor="w", 
                                         font=_label_font, fill=self.color)

class CameraPositionCalculator:
    def __init__(self, tags):
        self.tags = tags
        self.angle_between_tags = AngleBetweenTags(tags)
        self.a_deg = self.angle_between_tags.get_angle()
        self.a_rad = math.radians(self.a_deg)



class CameraPositionCalculatorDeprecated:
    def __init__(self, tags):
        self.tags = tags
        self.possible_camera_positions = []
        self.line_between_tags = LineBetweenTags(tags)
        self.angle_between_tags = AngleBetweenTags(tags)
        self.A_vector = self.line_between_tags.get_vector()
        self.A_mag = VectorUtils.int_magnitude(self.A_vector)
        self.a_deg = self.angle_between_tags.get_angle()
        self.a_rad = math.radians(self.a_deg)

        self.max_BC = self.calc_max_BC()

        self.angle_360_of_a_vector = VectorUtils.angle360(self.A_vector)
        self.quadrant_of_a_vector = VectorUtils.quadrant(self.A_vector)

    def calc(self):
        # A_vector points from T1 to T2
        # B_vector points from T2 to Possible Camera
        # C_vector points from T1 to Possible Camera
        #                 A
        #       T1----------------->T2
        #         \ b            c /
        #          \              /
        #           \            /
        #            \          /
        #           C \        / B
        #              \      /
        #               \    /
        #                \ a/
        #                 \/
        #           Possible Camera
        
        self.possible_camera_positions = []
        
        for C_mag in range(1, self.max_BC + 1, 1):
            res = {"A_vector": self.A_vector, "A_mag": self.A_mag, "a_rad": self.a_rad, "a_deg":self.a_deg, 
                   "C_mag": C_mag}
            
            # Law of sines
            res["c_rad"] = math.asin( C_mag * math.sin( self.a_rad ) / self.A_mag )
            res["c_deg"] = math.degrees(res["c_rad"])

            # Triangle sums to 180 degrees
            res["b_deg"] = 180 - res["c_deg"] - res["a_deg"]
            res["b_rad"] = math.radians(res["b_deg"])

            # Law of sines
            res["B_mag"] = res["A_mag"] * math.sin( res["b_rad"] ) / math.sin( res["a_rad"] ) 

            # C_vector
            tail_of_c_vector = VectorUtils.tail( res["A_vector"] )

            if self.quadrant_of_a_vector == 1 or self.quadrant_of_a_vector == 2 or self.quadrant_of_a_vector == 3:
                angle_of_c_vector = self.angle_360_of_a_vector - res["b_deg"]
            elif self.quadrant_of_a_vector == 4:
                angle_of_c_vector = self.angle_360_of_a_vector - res["b_deg"]

            res["C_vector"] = VectorUtils.vector_with_angle_and_magnitude(tail_of_c_vector, angle_of_c_vector, res["C_mag"])

            # B_vector
            res["B_vector"] = VectorUtils.tip( res["A_vector"] ) + VectorUtils.tip( res["C_vector"] )

            self.possible_camera_positions.append(res)

        return self.possible_camera_positions

    def calc_max_BC(self):
        # B and C are maximum magnitude when triangle is isocoles and b = c and B = C
        #                  A
        #       T1----------------->T2
        #         \ b            c /
        #          \              /
        #           \            /
        #            \          /
        #           C \        / B
        #              \      /
        #               \    /
        #                \ a/
        #                 \/
        #       Farthest possible Camera
        #
        # max =   A / ( 2 * sin(a/2) )
        return int( abs (self.A_mag / ( 2 * math.sin( float(self.a_rad / 2) ) ) ) )

class CameraPositionRender:
    def __init__(self, possible_camera_positions):
        self.positions = possible_camera_positions

    def render(self):

        coords = []
        curve = None
        for i, pos in enumerate(self.positions):
            if i%10 != 0:
                continue

            coord = VectorUtils.tip(pos["C_vector"])
            coords = coords + coord
            c_line = _canvas.create_line( pos["C_vector"][0], 
                                          pos["C_vector"][1], 
                                          pos["C_vector"][2], 
                                          pos["C_vector"][3], fill="orange" )  
            b_line = _canvas.create_line( pos["B_vector"][0], 
                                          pos["B_vector"][1], 
                                          pos["B_vector"][2], 
                                          pos["B_vector"][3], fill="orange"  )  

            if len(coords)>=4:
                curve = _canvas.create_line(*coords, fill="orange")
                
            _root.update()
            time.sleep(.001)
            _canvas.delete(b_line)
            _canvas.delete(c_line)
            if curve != None:
                _canvas.delete(curve)
            _root.update()

        _canvas.create_line(*coords, fill="orange")            

class _TagsSingleton:
    def __init__(self):
        self.tags = []
        self.lines_between_tags = []
        self.angles_between_tags = []

    def add_tag(self, x, y):
        self.tags.append(Tag(x, y, len(self.tags) + 1))

        if len(self.tags) > 1:
            last_2_tags = [self.tags[-2], self.tags[-1]]
            self.add_line_between_tags( last_2_tags )
            self.add_angle_between_tags( last_2_tags )

    def add_line_between_tags(self, tags):
        line = LineBetweenTags(tags)
        line.render()
        self.lines_between_tags.append(line)
    
    def add_angle_between_tags(self, tags):
        angle = AngleBetweenTags(tags)
        angle.render()
        self.angles_between_tags.append(angle)

    def get_num_tags(self):
        return len(self.tags)
    
    def get_tags(self):
        return self.tags
    
_tags_singleton = None 

def Tags():
    global _tags_singleton

    if _tags_singleton == None:
        _tags_singleton = _TagsSingleton()

    return _tags_singleton

class VectorUtils:

    @staticmethod
    def mean(numbers):
        return float(sum(numbers)) / max(len(numbers), 1)

    @staticmethod
    def int_mean(numbers):
        return int(VectorUtils.mean(numbers))

    @staticmethod
    def x_s(vector):
        return [vector[0], vector[2]]

    @staticmethod
    def y_s(vector):
        return [vector[1], vector[3]]

    @staticmethod
    def delta_x(vector):
        return  vector[2] - vector[0]

    @staticmethod
    def delta_y(vector):
        # Note signs feel backwards because canvas has Y increasing in the down direction but all trig
        # works with y increasing in the upward direction.
        return  - (vector[3] - vector[1])

    @staticmethod
    def midpoint(vector):
        return [ VectorUtils.int_mean( VectorUtils.x_s(vector) ), VectorUtils.int_mean( VectorUtils.y_s(vector) ) ]
    
    @staticmethod
    def magnitude(vector):
        diff_x_sq = (vector[0] - vector[2]) **2
        diff_y_sq = (vector[1] - vector[3]) **2
        return math.sqrt(diff_x_sq + diff_y_sq)

    @staticmethod
    def int_magnitude(vector):
        return int(VectorUtils.magnitude(vector))

    @staticmethod
    def quadrant(vector):
        dx = VectorUtils.delta_x(vector)
        dy = VectorUtils.delta_y(vector)

        if dx >= 0 and dy >= 0:
            result = 1
        elif dx < 0 and dy >= 0:
            result =  2
        elif dx < 0 and dy < 0:
            result =  3
        elif dx >= 0 and dy < 0:
            result =  4
        return result

    @staticmethod
    def angle(vector):
        rad = math.atan(float(VectorUtils.delta_y(vector)) / float(VectorUtils.delta_x(vector)))
        return  float(math.degrees(rad))

    @staticmethod
    def angle360(vector):
        quadrant = VectorUtils.quadrant(vector)
        angle = VectorUtils.angle(vector)

        if quadrant == 1:
            result = angle
        elif quadrant == 2:
            result = 180 + angle
        elif quadrant == 3:
            result = 180 + angle
        elif quadrant == 4:
            result = 360 + angle
        
        return result
    
    @staticmethod
    def vector_with_angle_and_magnitude(tail, angle, magnitude):
        delta_x = magnitude * math.cos(math.radians(angle))
        # Note negative becuase in canvas up is decreasing y.
        delta_y = - magnitude * math.sin(math.radians(angle))

        return [tail[0], tail[1], tail[0] + delta_x, tail[1] + delta_y]

    @staticmethod
    def tip(vector):
        return [vector[2], vector[3]]

    @staticmethod
    def tail(vector):
        return [vector[0], vector[1]]

tk.mainloop()
