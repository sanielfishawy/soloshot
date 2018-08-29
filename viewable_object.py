import math as math
import geometry_utils as GU
import random as random
from shapely.geometry import Polygon, Point, LineString
from simple_uid import SimpleUID

class ViewableObject:
    def __init__(self,
                 lifespan_num_timestamps=1000,
                 name=None
                 ):

        self.num_timestamps = lifespan_num_timestamps
        self.name = name
        self.id = SimpleUID().get_id()
        self.position_history = []
 
    def get_position_history(self):
        return self.position_history
    
    def get_position_history_len(self):
        return len(self.get_position_history())

    def get_position_at_time_stamp(self, timestamp):
        if timestamp >= self.get_position_history_len():
            r = None
        else:
            r = self.position_history[timestamp]
        
        return r
    
    def get_name(self):
        return self.name

class StationaryObject(ViewableObject):

    def __init__(self, position, **kwds):
        self.position = position
        super().__init__(**kwds)
        self.create_postion_history()

    def create_postion_history(self):
        self.position_history = [self.position] * self.num_timestamps
        return self

class MovingObject(ViewableObject):
    def __init__(self, 
                 boundary=None, # Boundary
                 max_dist_per_timestamp=10, 
                 min_dist_per_timestamp=9, 
                 twistyness_deg_per_timestamp=45,
                 **kwds
                ):

        self.max_dist_per_timestamp = max_dist_per_timestamp
        self.min_dist_per_timestamp = min_dist_per_timestamp
        self.max_deg_per_timestamp = twistyness_deg_per_timestamp
        self.max_rad_per_timestamp = math.radians(self.max_deg_per_timestamp)
        if boundary == None:
            raise "Moving object requires a boundary parameter of class Boundary"
        self.boundary = boundary
        super().__init__(**kwds)
    
        self.create_postion_history()

    def create_postion_history(self):
        ps = self.random_start_point()
        self.position_history.append(ps)
        self.position_history.append(GU.point_with_angle_and_distance_from_point(ps, 
                                                                                 self.boundary.angle_to_centroid(ps), 
                                                                                 self.random_distance()))

        for _ in range(2, self.num_timestamps):
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
        return self.last_angle() + r * self.max_rad_per_timestamp

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
        return random.random() * (self.max_dist_per_timestamp - self.min_dist_per_timestamp) + self.min_dist_per_timestamp
        

class Boundary(Polygon):
    
    def random_point(self):
        return random.choice(self.exterior.coords)
    
    def angle_to_centroid(self, point):
        return GU.angle_of_vector([point, self.centroid.coords[0]])

    def is_out_of_bounds(self, point):
        return not self.contains(Point(point))