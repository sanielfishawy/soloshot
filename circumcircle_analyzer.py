import math
from tag_position_analyzer import TagPositionAnalyzer
from image_analyzer import ImageAnalyzer 
from shapely.geometry import Point

class CircumcirleAnalyzer:

    def __init__(self, camera, tag, image_analyzer):
        self.camera = camera
        self.tag = tag
        self.image_analyzer = image_analyzer
        self.tag_position_analyzer = TagPositionAnalyzer(tag, camera)
        self.image_analyzer = ImageAnalyzer(camera)
        self.tag_gps_angle_threshold = math.radians(3)

    def get_frames(self):
        return self.tag_position_analyzer.get_frames_where_range_exceeds_threshold(self.tag_gps_angle_threshold)

    def setup_image_analyzer(self):
        self.image_analyzer.set_images(self.camera.get_image_generator().get_x_for_all_inview_objects_for_all_camera_time())
        return self
    
    def error_circle(self):
        return Point(self.camera.get_gps_position).buffer(self.camera.get_max_gps_error(), resolution=10000)
