from shapely.geometry import Point
import geometry_utils as GU

class Circumcircles:

    def __init__(
            self,
            early_postion,
            late_position,
            theta_rad,
            error_circle_center,
            error_circle_radius
    ):
        self.high_def_res = 10000
        self.low_def_res = 100

        self.error_circle_center = error_circle_center
        self.error_circle_radius = error_circle_radius
        self.theta_rad = theta_rad
        self.p1 = early_postion
        self.p2 = late_position

        self.circumcenters = None
        self.circumradius = None

        self.error_circle_exterior = None
        self.error_circle_disk = None

        self.c1_high_def = None
        self.c1_low_def = None

        self.c2_high_def = None
        self.c2_low_def = None

        self.c1_intersects_error_circle = None
        self.c2_intersects_error_circle = None

        self.c1_error_circle_intersection = None
        self.c2_error_circle_intersection = None

    def get_circumcenters(self):
        if self.circumcenters is None:
            self.circumcenters = GU.circumcenters(self.p1, self.p2, self.theta_rad)
        return self.circumcenters

    def get_circumradius(self):
        if self.circumradius is None:
            self.circumradius = GU.circumradius(self.p1, self.p2, self.theta_rad)
        return self.circumradius

    def get_error_circle_exterior(self):
        if self.error_circle_exterior is None:
            self.error_circle_exterior = Point(self.error_circle_center).buffer( #pylint: disable=no-member
                self.error_circle_radius,
                resolution=self.low_def_res
            ).exterior
        return self.error_circle_exterior

    def get_error_circle_disk(self):
        if self.error_circle_disk is None:
            self.error_circle_disk = Point(self.error_circle_center).buffer(
                self.error_circle_radius,
                resolution=self.high_def_res
            )
        return self.error_circle_disk

    def get_c1_low_def(self):
        if self.c1_low_def is None:
            self.c1_low_def = Point(self.get_circumcenters()[0]).buffer( #pylint: disable=no-member
                self.get_circumradius(),
                self.low_def_res
            ).exterior
        return self.c1_low_def

    def get_c2_low_def(self):
        if self.c2_low_def is None:
            self.c2_low_def = Point(self.get_circumcenters()[1]).buffer( #pylint: disable=no-member
                self.get_circumradius(),
                self.low_def_res
            ).exterior
        return self.c2_low_def

    def get_c1_high_def(self):
        if self.c1_high_def is None:
            self.c1_high_def = Point(self.get_circumcenters()[0]).buffer( #pylint: disable=no-member
                self.get_circumradius(),
                self.high_def_res
            ).exterior
        return self.c1_high_def

    def get_c2_high_def(self):
        if self.c2_high_def is None:
            self.c2_high_def = Point(self.get_circumcenters()[1]).buffer( #pylint: disable=no-member
                self.get_circumradius(),
                self.high_def_res
            ).exterior
        return self.c2_high_def

    def get_c1_intersects_error_circle(self):
        if self.c1_intersects_error_circle is None:
            self.c1_intersects_error_circle = self.get_c1_low_def().intersects(
                self.get_error_circle_exterior()
            )
        return self.c1_intersects_error_circle

    def get_c2_intersects_error_circle(self):
        if self.c2_intersects_error_circle is None:
            self.c2_intersects_error_circle = self.get_c2_low_def().intersects(
                self.get_error_circle_exterior()
            )
        return self.c2_intersects_error_circle

    def get_intersects_error_circle(self):
        return self.get_c1_intersects_error_circle() or self.get_c2_intersects_error_circle()

    def get_c1_error_circle_intersection(self):
        if self.c1_error_circle_intersection is None and self.get_c1_intersects_error_circle():
            self.c1_error_circle_intersection = self.get_c1_high_def().intersection(
                self.get_error_circle_disk()
            )
        return self.c1_error_circle_intersection

    def get_c2_error_circle_intersection(self):
        if self.c2_error_circle_intersection is None and self.get_c2_intersects_error_circle():
            self.c2_error_circle_intersection = self.get_c2_high_def().intersection(
                self.get_error_circle_disk()
            )
        return self.c2_error_circle_intersection

    def get_error_circle_intersection(self):
        if self.get_c1_error_circle_intersection() is not None:
            return self.get_c1_error_circle_intersection()
        return self.get_c2_error_circle_intersection()
