import math as math
import geometry_utils as GU
import random as random
from shapely.geometry import Polygon, Point, LineString

class MovingObject:
    def __init__(self, 
                 boundary, # Boundary
                 max_speed_fps=10, 
                 min_speed_fps=9, 
                 twistyness_deg_ps=45, 
                 frames_per_second=3,
                 video_length_sec=1000):

        self.max_speed = max_speed_fps
        self.min_speed = min_speed_fps
        self.twistyness_deg = twistyness_deg_ps
        self.frps = frames_per_second
        self.boundary = boundary
        self.video_length = video_length_sec
    
        self.calc_intermediate_variables()
        self.position_history = []
        self.create_postion_history()

    def get_position_history(self):
        return self.position_history

    def calc_intermediate_variables(self):
        self.num_frames = self.frps * self.video_length
        self.twistyness_rad = math.radians(self.twistyness_deg)
        self.max_angle_change_per_frame_rad = self.twistyness_rad / self.frps
        self.max_distance_per_frame = self.max_speed / self.frps
        self.min_distance_per_frame = self.min_speed / self.frps

    def create_postion_history(self):
        ps = self.random_start_point()
        self.position_history.append(ps)
        self.position_history.append(GU.point_with_angle_and_distance_from_point(ps, 
                                                                                 self.boundary.angle_to_centroid(ps), 
                                                                                 self.random_distance()))

        for _ in range(2, self.num_frames):
            self.add_point_to_history()


    def add_point_to_history(self):
        if self.boundary.is_out_of_bounds(self.last_point()):
            a = self.boundary.angle_to_centroid(self.last_point())
        else:
            a = self.random_angle()
        
        d = self.random_distance()
        p = GU.point_with_angle_and_distance_from_point(self.last_point(), a, d)
        self.position_history.append(p)

    def random_angle(self):
        r = random.random() * 2 - 1
        return self.last_angle() + r * self.twistyness_rad

    def last_angle(self):
        return GU.angle_of_vector(self.last_segment())

    def last_segment(self):
        if len(self.position_history) < 2:
            return None
        else:
            return [self.position_history[-2], self.last_point()]

    def last_point(self):
        return self.position_history[-1]

    def random_start_point(self):
        return self.boundary.random_point()
    
    def random_distance(self):
        return random.random() * (self.max_distance_per_frame - self.min_distance_per_frame) + self.min_distance_per_frame
        

class Boundary(Polygon):
    
    def random_point(self):
        return random.choice(self.exterior.coords)
    
    def angle_to_centroid(self, point):
        return GU.angle_of_vector([point, self.centroid.coords[0]])

    def is_out_of_bounds(self, point):
        return not self.contains(Point(point))