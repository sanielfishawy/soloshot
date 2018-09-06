from shapely.geometry import LineString
from computer_vision import ComputerVision
import math
import geometry_utils as GUtils

class ImageGenerator:

#  | <------------ i_w --------------> |
#  | <--- i_w/2 ---> |
#  
#           | <- x ->|
#                   i_c
#   --------.--------+-----------------
#   \                |                /
#    \       .       |               / 
#     \              |              / 
#      \      .      |             /   
#       \            |d           /       
#        \     .     |           /       
#         \          |          /
#          \    v    |         / 
#           \    .   |        /    
#            \       |       /
#             \   .  |      /
#              \     |     /
#               \  . |    /
#                \   |   /
#     theta --------.|  /
#                  \ | / ------- fov
#                   \|/
#                    +
#                    c
# 
#  c = camera
#  i_w = image_width
#  d = length in direction of camera pan angle to create image width
#  fov = field of view angle
#  v = viewable object
#  x = vector from center of image to projected viewable object
#  i_c = point at the center of the image
#           i_w  
#  d =  -------------
#       2 * tan(fov/2)
# 
#  x = d * tan2(theta)
#
#
#  i_c
#    +
#     \
#      \
#       \
#        \
#         \
#          \
#           \ 
#            \ camera_pan_angle
#             +-----------------------------
#             c
#
#

    def __init__(self, image_width=640):
        self.i_w = image_width
    
    def set_camera(self, camera):
        self.camera = camera
        self.setup_for_camera()

    def setup_for_camera(self):
        self.fov = self.camera.get_fov_rad()
        self.half_fov = self.fov / 2
        self.d = self.i_w / (2 * math.tan(self.half_fov))
        return self
    
    def get_d(self):
        return self.d

    def get_x_for_all_inview_objects_for_all_camera_time(self):
        r = []
        for timestamp in range(self.camera.get_state_history_len()):
            r.append(self.get_x_for_all_inview_objects_at_timestamp(timestamp))
        return r

    def get_x_for_all_inview_objects_at_timestamp(self, timestamp):
        r = {}
        for obj in self.camera.get_objects_in_view(timestamp):
            r[obj] = self.get_x_for_inview_object_at_timestamp(obj, timestamp)
        
        return r

    def get_x_for_inview_object_at_timestamp(self, obj, timestamp):
        if not self.camera.is_object_in_view(obj, timestamp):
            raise "Object not in view"
        
        return self.d * math.tan( self.get_theta_rad(obj, timestamp) )
        
    def get_theta_rad(self, obj, timestamp):
        o_pos = obj.get_position_at_timestamp(timestamp)
        c_pos = self.camera.get_actual_position()
        i_c_pos = self.get_i_c(timestamp)
        return GUtils.signed_subtended_angle_from_p1_to_p2_rad(c_pos, i_c_pos, o_pos)

    def get_i_c(self, timestamp):
        return GUtils.point_with_angle_and_distance_from_point(self.camera.get_actual_position(), 
                                                               self.camera.get_actual_pan_angle_rad(timestamp), 
                                                               self.d)