import unittest
import geometry_utils as GU
import sympy.geometry as Geo
from sympy import *
import math

class TestGeometryUtilsIsosceles(unittest.TestCase):
    
    def setUp(self): 
        # Set up a segment in each quadrant with varying angles
        thetas = [10, 30, 90, 150]

        pc = Geo.Point(100,100)
        
        ps = [ (110, 120), 
               (95, 113),
               (85, 75),
               (115, 65) ]

        self.cases = []

        for i, point in enumerate(ps):
            case = {}
           
            case["theta"] = thetas[i]
            
            a = Geo.Segment(pc, point)
            case["a"] = a

            r1, r2 = GU.isosceles_points(a.p1, a.p2, thetas[i])
            case["r"] = Geo.Segment(r1, r2)
            self.cases.append(case)

    def test_r_a_are_perpendicular(self):
        for case in self.cases:
            a,r = case["a"], case["r"]
            self.assertAlmostEqual(a.smallest_angle_between(r).evalf(), N(pi/2))

    def test_r_and_a_intersect_at_midpoint(self):
        for case in self.cases:
            a,r = case["a"], case["r"]
            mid_a = a.midpoint
            mid_r = r.midpoint
            self.assertAlmostEqual( mid_a.x.evalf(), mid_r.x.evalf() )
            self.assertAlmostEqual( mid_a.y.evalf(), mid_r.y.evalf() )

    def test_r_correct_length(self):
        for case in self.cases:
            a,r,theta = case["a"], case["r"], case["theta"]
            _tan = tan(math.radians(theta/2)).evalf()
            half_a = (0.5 * a.length).evalf()
            half_r = (0.5 * r.length).evalf()

            self.assertAlmostEquals(_tan, half_a / half_r)

if __name__ == '__main__':
    unittest.main()