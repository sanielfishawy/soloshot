import math
import sympy.geometry as Geo

def isosceles_points(p1, p2, theta_deg):
    # DEPRECATED: This method is not currently used
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

        
#          Circum...        
#            theta_deg
#               /\
#              /  \
#             /    \
#            /      \
#           p1      p2
def circumcenters(p1, p2, theta_deg):
    radius = circumradius(p1, p2, theta_deg)
    c1 = Geo.Circle(p1, radius)
    c2 = Geo.Circle(p2, radius)
    return Geo.intersection(c1, c2)

def circumcircles(p1, p2, theta_deg):
    (c1, c2) = circumcenters(p1, p2, theta_deg)
    radius = circumradius(p1, p2, theta_deg)
    return (Geo.Circle(c1, radius), Geo.Circle(c2, radius))

def circumradius(p1, p2, theta_deg):
    return 0.5 * circumdiameter(p1, p2, theta_deg)
    
def circumdiameter(p1, p2, theta_deg):
    s = Geo.Segment(p1, p2)
    return ( s.length / math.sin(math.radians(theta_deg)) ).evalf()

def subtended_angle_rad(v, p1, p2):
    s1 = Geo.Segment(v, p1)
    s2 = Geo.Segment(v, p2)
    return s1.smallest_angle_between(s2).evalf()

def subtended_angle_deg(v, p1, p2):
    return math.degrees(subtended_angle_rad(v, p1, p2))

def signed_subtended_angle_from_p1_to_p2_rad(v, p1, p2):
    a1 = angle_of_vector_360_rad((v, p1))
    a2 = angle_of_vector_360_rad((v, p2))
    r = a2 - a1
    if r > math.pi:
        r = - (2 * math.pi - r)
    if r < -math.pi: 
        r = 2 * math.pi + r
    return r

def quadrant_of_vector(p1, p2):
    p1_x, p1_y = p1
    p2_x, p2_y = p2
    
    if (p2_x >= p1_x):
        if (p2_y >= p1_y):
            return 1
        else:
            return 4
    else:
        if (p2_y >= p1_y):
            return 2
        else:
            return 3

def angle_of_vector_between_points(p1, p2):
    return angle_of_vector((p1, p2))

def angle_of_vector(coords):
    p1, p2 = coords
    p1_x, p1_y = p1
    p2_x, p2_y = p2
    if (p2_x == p1_x):
        if (p2_y == p1_y):
            r = None
        elif (p2_y > p1_y):
            r = math.pi / 2
        elif (p2_y < p1_y):
            r = -math.pi / 2
    else:
        r = math.atan2( (p2_y - p1_y), (p2_x - p1_x) )

    return r

def angle_of_vector_360_rad(coords):
    p1, p2 = coords
    angle = angle_of_vector(coords)
    if quadrant_of_vector(p1, p2) == 3 or quadrant_of_vector(p1, p2) == 4:
        angle = 2 * math.pi + angle
    return angle

def angel_of_vector_between_points_360_rad(p1,p2):
    return angle_of_vector_360_rad((p1, p2))

def point_with_angle_and_distance_from_point(point, angle_rad, d):
    return (point[0] + d * math.cos(angle_rad), (point[1] + d * math.sin(angle_rad)))
    