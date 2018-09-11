import math
from image_generator import ImageGenerator

#       |------------x1----------0----------------------x2-|
#                     .          |                    .                 
#                      .         |                  .                   
#                       .        | d              .                     
#                        .       |              .                       
#                         .      |            .                         
#                          .     |          .                           
#                           .    |        .                             
#                            . a1|  a2  .                               
#                             .  |    .                                 
#                              . |  .                                   
#                               .|.                                     
#                                c
#
# 
# Moving from left to right gives postive subtended angles
# Moving from right to left gives negatie subtended angles
# x from image generator may be positive (right of center screen) e.g. x2 or negative (left of center screen) e.g. x1
#
class ImageAnalyzer:

    def __init__(self, camera):
        self.camera = camera
        self.images = None
        self.d = None

    def set_images(self, images):
        self.images = images
        return self

    def get_subtended_angles_for_all_objects(self, timestamp1, timestamp2):
        objs_1 = self.images[timestamp1].keys()
        objs_2 = self.images[timestamp2].keys()
        objs = [obj for obj in objs_1 if obj in objs_2]

        r = {}
        for obj in objs:
            r[obj] = self._get_subtended_angle_with_obj_timestamps_rad(obj, timestamp1, timestamp2)
            
        return r

    def _get_x_with_object_and_timestamp(self, obj, timestamp):
        return self.images[timestamp][obj]

    def _get_subtended_angle_with_obj_timestamps_rad(self, obj, timestamp1, timestamp2):
        x1 = self.images[timestamp1].get(obj, None)
        x2 = self.images[timestamp2].get(obj, None)

        if x1 == None or x2 == None:
            return None
        else:
            return self._get_subtended_angle_with_x_rad(x1, x2)
    
    def _get_subtended_angle_with_x_rad(self, x1, x2):
        a1 = math.atan2(x1, self.get_d())
        a2 = math.atan2(x2, self.get_d())
        return a2 - a1
    
    def _calc_d(self):
        return self.camera.get_image_generator().get_image_width() / 2 / math.tan(self.camera.get_fov_rad() / 2)
    
    def get_d(self):
        if self.d == None:
            self.d = self._calc_d()
        return self.d