from shapely.geometry import Polygon, Point
import geometry_utils as GU
import random

class Boundary(Polygon):
    
    def random_point(self):
        return random.choice(self.exterior.coords)
    
    def angle_to_centroid(self, point):
        return GU.angle_of_vector([point, self.centroid.coords[0]])

    def is_out_of_bounds(self, point):
        return not self.contains(Point(point))