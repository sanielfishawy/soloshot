from shapely.geometry import Polygon, Point
from object_universe import ObjectUniverse

class ViewTriangle(Polygon):

    def objects_in_view(self, timestamp):
        objects = ObjectUniverse().get_objects(timestamp)
        return list( filter(lambda obj: self.object_is_in_view(obj, timestamp), objects) )
    

    def object_is_in_view(self, obj, timestamp):
        return self.contains( Point(obj.get_position_at_time_stamp(timestamp)) )
