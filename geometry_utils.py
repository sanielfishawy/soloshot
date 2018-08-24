import math
import sympy.geometry as Geo

def isosceles_points(p1, p2, theta_deg):
    #             r1
    #             +
    #            /|\
    #           / | \
    #          /  |d \
    #         /   |   \
    #        / a/2|a/2 \
    #    p1 x-----+-----x p2
    #        \    |    /
    #         \   |   /
    #          \  |d /
    #           \ | /
    #            \|/
    #             +
    #             r2
    a = Geo.Segment(p1, p2)
    half_a = a.length.evalf() / 2.0
    mp = a.midpoint
    r_slope = a.perpendicular_bisector().slope.evalf()  #pylint: disable=no-member
    
    half_theta_deg = theta_deg / 2.0
    half_theta_rad = math.radians(half_theta_deg)
    d = half_a / math.tan(half_theta_rad)
    
    dx = d / math.sqrt(1 + r_slope**2)
    dy = -dx * r_slope

    r1 = (mp.x.evalf() - dx, mp.y.evalf() + dy)  #pylint: disable=no-member
    r2 = (mp.x.evalf() + dx, mp.y.evalf() - dy)  #pylint: disable=no-member
    return (r1, r2)
