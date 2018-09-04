import math 
from shapely.geometry import Polygon
import geometry_utils as GU
from view_triangle import ViewTriangle

class Camera:

    def __init__(self,
                 num_timestamps=1000,
                 actual_position=(0,0),
                 gps_position=(0,0),
                 gps_max_error=(6),
                 compass_error_deg=0,
                 fov_deg=67,
                 range=2000,
                 computer_vision=None,
                 object_universe = None,
                 ):

        self.actual_position = actual_position
        self.gps_position = gps_position
        self.gps_max_error = gps_max_error
        self.compass_error_deg = compass_error_deg
        self.compass_error_rad = math.radians(self.compass_error_deg)
        self.fov_deg = fov_deg
        self.range = range
        self.computer_vision = computer_vision
        self.object_universe = object_universe

        self.num_timestamps = num_timestamps
        self.init_state_history()

    def get_num_timestamps(self):
        return self.num_timestamps

    def set_num_timestamps(self, n):
        self.num_timestamps = n
        self.adjust_state_history_to_num_timestamps()
        self.notify_computer_vision_of_timestamp_adjustment()
        return self

    def get_actual_position(self):
        return self.actual_position

    def set_actual_position(self, actual_position):
        self.actual_position = actual_position
        return self

    def set_gps_position(self, gps_position):
        self.gps_position = gps_position
        return self

    def get_gps_position(self):
        return self.gps_position

    def set_gps_max_error(self, gps_max_error):
        self.gps_max_error = gps_max_error
        return self

    def get_gps_max_error(self):
        return self.gps_max_error
    
    def set_fov_deg(self, fov_deg):
        self.fov_deg = fov_deg
        return self
    
    def get_fov_deg(self):
        return self.fov_deg

    def set_fov_rad(self, fov_rad):
        self.fov_deg = math.radians(fov_rad)
        return self
    
    def get_fov_rad(self):
        return math.radians(self.fov_deg)

    def set_object_universe(self, object_universe):
        self.object_universe = object_universe
        return self

    def get_object_universe(self):
        return self.object_universe

    def set_computer_vision(self, computer_vision):
        self.computer_vision = computer_vision
        self.computer_vision.set_camera(self)
        return self

    def get_computer_vision(self):
        return self.computer_vision

    def init_state_history(self):
        self.state_history = [{'motor_pan_angle_deg': 0}]
        self.adjust_state_history_to_num_timestamps()

    def notify_computer_vision_of_timestamp_adjustment(self):
        if self.computer_vision:
            self.computer_vision.camera_num_timestamps_changed()
    
    def adjust_state_history_to_num_timestamps(self):
        if self.get_num_timestamps() > self.get_state_history_len():
            self.extend_state_history()
        elif self.get_num_timestamps() < self.get_state_history_len():
            self.truncate_state_history()
        return self
    
    def extend_state_history(self):
        self.state_history += [None] * (self.get_num_timestamps() - self.get_state_history_len())
        return self
    
    def truncate_state_history(self):
        self.state_history = self.state_history[0: self.get_num_timestamps()]

    def get_state_history_len(self):
        return len(self.get_state_history())
    
    def get_state_history(self):
        return self.state_history
    
    def get_state_at_timestamp(self, timestamp):
        return self.get_state_history()[timestamp]
    
    def set_state_of_pan_motor_angle_at_timestamp(self, angle_deg, timestamp):
        if self.get_state_at_timestamp(timestamp) == None:
            self.get_state_history()[timestamp] = {}

        self.get_state_history()[timestamp]['motor_pan_angle_deg'] = angle_deg

    def get_motor_pan_angle_deg(self, timestamp):
        h = self.get_state_history_at_time(timestamp)
        if h == None:
            return None
        else:
            return h['motor_pan_angle_deg']
    
    def get_motor_pan_angle_rad(self, timestamp):
        a = self.get_motor_pan_angle_deg(timestamp)
        if a == None:
            return None
        else:
            return math.radians(a)
    
    def get_state_history_at_time(self, timestamp):
        return self.state_history[timestamp]

    def get_actual_pan_angle_deg(self, timestamp):
        return self.get_motor_pan_angle_deg(timestamp) + self.compass_error_deg

    def get_actual_pan_angle_rad(self, timestamp):
        return math.radians(self.get_actual_pan_angle_deg(timestamp))

    def get_objects_in_view(self, timestamp):
        if self.get_state_at_timestamp(timestamp) == None:
            return []
        else:
            return self.get_view_triangle(timestamp).objects_in_view(timestamp, self.object_universe)

    def get_objects_out_view(self, timestamp):
        if self.get_state_at_timestamp(timestamp) == None:
            return self.object_universe.get_viewable_objects()
        else:
            return self.get_view_triangle(timestamp).objects_out_view(timestamp, self.object_universe)

    def get_view_triangle(self, timestamp):
        return ViewTriangle([self.actual_position, 
                             self.left_of_frame_angle_point(timestamp), 
                             self.right_of_frame_angle_point(timestamp)])

    def left_of_frame_angle_rad(self, timestamp):
        return self.get_actual_pan_angle_rad(timestamp) + ( self.get_fov_rad() / 2 ) 

    def left_of_frame_angle_deg(self, timestamp):
        return math.degrees(self.left_of_frame_angle_deg(timestamp))
        
    def right_of_frame_angle_rad(self, timestamp):
        return self.get_actual_pan_angle_rad(timestamp) - ( self.get_fov_rad() / 2 ) 

    def right_of_frame_angle_deg(self, timestamp):
        return math.degrees(self.right_of_frame_angle_deg(timestamp))

    def left_of_frame_angle_point(self, timestamp):
        return GU.point_with_angle_and_distance_from_point(self.actual_position, 
                                                           self.left_of_frame_angle_rad(timestamp), 
                                                           self.range)
        
    def right_of_frame_angle_point(self, timestamp):
        return GU.point_with_angle_and_distance_from_point(self.actual_position, 
                                                           self.right_of_frame_angle_rad(timestamp), 
                                                           self.range)
        
    def set_pan_angle_deg(self, angle_deg, timestamp):
        self.set_state_of_pan_motor_angle_at_timestamp(angle_deg, timestamp)
        return self

    def set_pan_angle_rad(self, angle_rad, timestamp):
        self.set_pan_angle_deg(math.degrees(angle_rad), timestamp)
        return self
    
    def get_pan_angle_deg(self, timestamp):
        return self.get_pan_angle_deg(timestamp)
    
    def get_pan_angle_rad(self, timestamp):
        return math.radians(self.get_pan_angle_deg(timestamp))


