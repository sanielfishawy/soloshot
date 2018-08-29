import math 
from shapely.geometry import Polygon
from object_universe import ObjectUniverse
import geometry_utils as GU
from view_triangle import ViewTriangle

class Camera:

    def __init__(self,
                 actual_position=(0,0),
                 gps_position=(0,0),
                 compass_error_deg=0,
                 fov_deg=67,
                 range=2000):

        self.motor_pan_angle_deg = 0
        self.actual_position = actual_position
        self.gps_position = gps_position
        self.compass_error_deg = compass_error_deg
        self.compass_error_rad = math.radians(self.compass_error_deg)
        self.fov_deg = fov_deg
        self.fov_rad = math.radians(self.fov_deg)
        self.range = range

    def get_actual_pan_angle_deg(self):
        return self.motor_pan_angle_deg + self.compass_error_deg

    def get_actual_pan_angle_rad(self):
        return math.radians(self.get_actual_pan_angle_deg())

    def objects_in_view(self):
        return self.get_view_triangle().objects_in_view()

    def get_view_triangle(self):
        return ViewTriangle([self.actual_position, 
                             self.left_of_frame_angle_point(), 
                             self.right_of_frame_angle_point()])

    def left_of_frame_angle_rad(self):
        return self.get_actual_pan_angle_rad + ( self.fov_rad / 2 ) 

    def left_of_frame_angle_deg(self):
        return math.degrees(self.left_of_frame_angle_deg())
        
    def right_of_frame_angle_rad(self):
        return self.get_actual_pan_angle_rad - ( self.fov_rad / 2 ) 

    def right_of_frame_angle_deg(self):
        return math.degrees(self.right_of_frame_angle_deg())

    def left_of_frame_angle_point(self):
        return GU.point_with_angle_and_distance_from_point(self.actual_position, 
                                                           self.left_of_frame_angle_rad(), 
                                                           self.range)
        
    def right_of_frame_angle_point(self):
        return GU.point_with_angle_and_distance_from_point(self.actual_position, 
                                                           self.right_of_frame_angle_rad(), 
                                                           self.range)
        
    def set_pan_angle_deg(self, angle_deg):
        self.pan_angle_deg = angle_deg

    def set_pan_angle_rad(self, angle_rad):
        self.set_pan_angle_deg(math.degrees(angle_rad))
    
    def get_pan_angle_deg(self):
        return self.pan_angle_deg
    
    def get_pan_angle_rad(self):
        return math.radians(self.get_pan_angle_deg())


