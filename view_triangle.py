from shapely.geometry import Polygon, Point
from object_universe import ObjectUniverse

class ViewTriangle(Polygon):

    def objects_in_view(self, time_stamp):
        objects = ObjectUniverse().get_objects(time_stamp)
        return list( filter(lambda obj: self.object_is_in_view(obj, time_stamp), objects) )
    

    def object_is_in_view(self, obj, time_stamp):
        return self.contains( Point(obj.get_position_at_time_stamp(time_stamp)) )