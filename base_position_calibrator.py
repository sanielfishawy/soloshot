import math
from shapely.geometry import Point, LineString, MultiPoint

from camera import Camera
from object_stats_processor import ObjectsStatsProcessor
from object_motion_analyzer import ObjectMotionAnalyzer
from tag_position_analyzer import TagPositionAnalyzer
from viewable_object import ViewableObject

class BasePositionCalibrator:

    def __init__(self, camera, tag, tag_gps_angle_threshold=math.radians(3)):
        '''
        :param Camera camera:
        :param ViewableObject tag:
        '''
        self._camera = camera
        self._tag = tag
        self._tag_gps_angle_threshold = tag_gps_angle_threshold

        self._object_motion_analyzer = ObjectMotionAnalyzer(self._camera,
                                                           self._tag,
                                                           self._tag_gps_angle_threshold)
        
        self._object_stats_processor = ObjectsStatsProcessor(self._object_motion_analyzer)

        self._error_circle_intersections = None #cached for speed

    def get_camera(self):
        return self._camera
    
    def get_tag(self):
        return self._tag
    
    def get_tag_gps_angle_threshold(self):
        return self._tag_gps_angle_threshold
    
    def get_object_motion_analyzer(self):
        '''
        :rtype ObjectMotionAnalyzer
        '''
        return self._object_motion_analyzer
    
    def get_object_stats_processor(self):
        '''
        :rtype ObjectStatsProcessor
        '''
        return self._object_stats_processor

    def get_base_position_point(self):
        return Point(self._get_points_where_error_circle_intersections_intersect_each_other().centroid)
    
    def get_base_position(self):
        p = self.get_base_position_point()
        return (p.x, p.y)

    def get_tag_candidate(self):
        if len(self.get_object_stats_processor().get_top_ranked_objects()) > 1:
            raise 'code not written to handle more than one top_ranked_object'

        return self.get_object_stats_processor().get_top_ranked_object()

    def _get_points_where_error_circle_intersections_intersect_each_other(self):
        '''
        :rtype MultiPoint
        '''
        points = []
        for a in self._get_all_error_circle_intersections():
            for b in self._get_all_error_circle_intersections():
                if a != b:
                    isect = a.intersection(b)
                    if type(isect) == Point: # Ignore similar circumcircles which intersect in mulitple points and would smear the results.
                        points.append(a.intersection(b))
        return MultiPoint(points=points)
        
    def _get_all_error_circle_intersections(self):
        if self._error_circle_intersections == None:
            self._error_circle_intersections = [cc.get_error_circle_intersection() for cc in self._get_all_circumcircle_objects()]
        return self._error_circle_intersections
    
    def _get_all_circumcircle_objects(self):
        ccs = self.get_object_motion_analyzer().get_circumcircles_for_object_for_all_frames(self.get_tag_candidate())
        ccs_with_tag_candidate_in_frame = list(filter(lambda cc: cc != None, ccs))
        return ccs_with_tag_candidate_in_frame
        

