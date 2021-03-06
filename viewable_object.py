import math
import random
import geometry_utils as GU
from simple_uid import SimpleUID

class ViewableObject:
    def __init__(self,
                 num_timestamps=1000,
                 name=None
                 ):

        self.num_timestamps = num_timestamps
        self.name = name
        self.id = SimpleUID().get_id()
        self.position_history = []
        self.create_position_history()
        self.is_tag = False

    def get_is_tag(self):
        return self.is_tag

    def set_num_timestamps(self, n):
        self.num_timestamps = n
        pos_len = self.get_position_history_len()

        if pos_len == 0:
            self.create_position_history()
        elif pos_len > self.num_timestamps:
            self.position_history = self.position_history[0: self.num_timestamps]
        elif pos_len < self.num_timestamps:
            self.create_position_history()

        return self

    def get_num_timestamps(self):
        return self.num_timestamps

    def create_position_history(self):
        self.position_history = [None] * self.num_timestamps
        return self

    def clear_postion_history(self):
        self.position_history = []
        return self

    def get_position_history(self):
        return self.position_history

    def get_position_history_len(self):
        return len(self.get_position_history())

    def get_position_at_timestamp(self, timestamp):
        if timestamp >= self.get_position_history_len():
            r = None
        else:
            r = self.position_history[timestamp]

        return r

    def set_position_at_timestamp(self, pos, timestamp):
        self.get_position_history()[timestamp] = pos
        return self

    def get_name(self):
        return self.name

class StationaryObject(ViewableObject):

    def __init__(self, position, **kwds):
        self.position = position
        super().__init__(**kwds)
        self.create_position_history()

    def create_position_history(self):
        self.position_history = [self.position] * self.num_timestamps
        return self

class RandomlyMovingObject(ViewableObject):
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
        self.clear_postion_history()
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


class RandomlyMovingTag(RandomlyMovingObject):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.is_tag = True


class ViewableObjects:
    def __init__(self, viewable_objects=[]):
        self._viewable_objects = viewable_objects

    def set_viewable_objects(self, viewable_objects):
        if type(viewable_objects) != list:
            self._viewable_objects = [viewable_objects]
        else:
            self._viewable_objects = viewable_objects
        return self

    def get_viewable_objects(self):
        return self._viewable_objects
