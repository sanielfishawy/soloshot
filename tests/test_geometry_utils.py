import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
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

            self.assertAlmostEqual(_tan, half_a / half_r)
    
    def test_angle_of_vector(self):
        p0 = (0,0)
        p1_s = [(0,0),
                (1,0),
                (1,1), 
                (0,1), 
                (-1,1), 
                (-1,0), 
                (-1,-1), 
                (0,-1), 
                (1,-1)] 

        results =  [None,
                    0,
                    math.pi / 4,
                    math.pi / 2,
                    3 * math.pi / 4,
                    math.pi,
                    -( 3 * math.pi / 4),
                    - math.pi / 2,
                    - math.pi / 4]
        
        for i, p1 in enumerate(p1_s):
            self.assertAlmostEqual(GU.angle_of_vector([p0, p1]), results[i])

    def test_angel_of_vector_between_points_360_rad(self):
        p0 = (0,0)
        p1_s = [(0,0),
                (1,0),
                (1,1), 
                (0,1), 
                (-1,1), 
                (-1,0), 
                (-1,-1), 
                (0,-1), 
                (1,-1)] 

        results =  [None,
                    0,
                    math.pi / 4,
                    math.pi / 2,
                    3 * math.pi / 4,
                    math.pi,
                    5 * math.pi / 4,
                    3 * math.pi / 2,
                    7 * math.pi / 4]
        
        for i, p1 in enumerate(p1_s):
            self.assertAlmostEqual(GU.angel_of_vector_between_points_360_rad(p0, p1), results[i]) 

    def test_point_with_angle_and_distance_to_point(self):

        p0 = (1,1)

        d = 1
        rt2_2 = math.sqrt(2) / 2

        angles = [0,
                  math.pi / 4,
                  math.pi / 2,
                  3 * pi / 4,
                  math.pi,
                  -3 * math.pi / 4, 
                  -math.pi / 2,
                  -math.pi / 4]
        
        expect_s = [(2,1),
                    (1 + rt2_2, 1 + rt2_2),
                    (1, 2),
                    (1 - rt2_2, 1 + rt2_2),
                    (0, 1),
                    (1 - rt2_2, 1 - rt2_2),
                    (1, 0),
                   (1 + rt2_2, 1 - rt2_2)]
        
        for i, angle in enumerate(angles):
            r = GU.point_with_angle_and_distance_from_point(p0, angle, d)
            expect = expect_s[i]
            self.assertAlmostEqual(r[0], expect[0])
            self.assertAlmostEqual(r[1], expect[1])

    def test_quadrant(self):
        v = (1,1)
        p1_s = [(2,2),(0,2),(0,0),(2,0)]
        p2_s = p1_s

        for i, p in enumerate(p1_s):
            self.assertEqual(GU.quadrant_of_vector(v, p), i+1)

    def test_signed_subtended_angle_from_p1_to_p2_rad(self):
        v = (1,1)
        p1_s = [(2,2),(0,2),(0,0),(2,0)]
        p2_s = p1_s

        for p1_i, p1 in enumerate(p1_s):
            for p2_i, p2 in enumerate(p2_s):
                s_angle = GU.signed_subtended_angle_from_p1_to_p2_rad(v, p1, p2)
                q1 = GU.quadrant_of_vector(v, p1)
                q2 = GU.quadrant_of_vector(v, p2)

                if p1_i == p2_i:
                    self.assertEqual(s_angle, 0)
                if q1 == 1:
                    if q2 == 2:
                        self.assertAlmostEqual(s_angle, math.pi / 2)
                    elif q2 == 3:
                        self.assertAlmostEqual(s_angle, math.pi)
                    elif q2 == 4:
                        self.assertAlmostEqual(s_angle, -math.pi / 2)
                if q1 == 2:
                    if q2 == 1:
                        self.assertAlmostEqual(s_angle, -math.pi / 2)
                    elif q2 == 3:
                        self.assertAlmostEqual(s_angle, math.pi / 2)
                    elif q2 == 4:
                        self.assertAlmostEqual(s_angle, math.pi)
                if q1 == 3:
                    if q2 == 1:
                        self.assertAlmostEqual(s_angle, - math.pi)
                    elif q2 == 2:
                        self.assertAlmostEqual(s_angle, -math.pi / 2)
                    elif q2 == 4:
                        self.assertAlmostEqual(s_angle, math.pi / 2)
                if q1 == 4:
                    if q2 == 1:
                        self.assertAlmostEqual(s_angle, math.pi / 2)
                    elif q2 == 2:
                        self.assertAlmostEqual(s_angle, -math.pi)
                    elif q2 == 3:
                        self.assertAlmostEqual(s_angle, -math.pi / 2)

if __name__ == '__main__':
    unittest.main()