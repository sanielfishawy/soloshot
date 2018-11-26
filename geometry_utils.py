import math
from shapely.geometry import Point


#          Circum...
#            theta_deg
#               /\
#              /  \
#             /    \
#            /      \
#           p1      p2

def circumcenters(p1, p2, theta_rad):
    radius = circumradius(p1, p2, abs(theta_rad))
    c1 = Point(p1).buffer(radius, resolution=10000).exterior #pylint: disable=no-member
    c2 = Point(p2).buffer(radius, resolution=10000).exterior #pylint: disable=no-member
    return [(p.x, p.y) for p in c1.intersection(c2)]

def circumradius(p1, p2, theta_rad):
    return 0.5 * circumdiameter(p1, p2, abs(theta_rad))

def circumdiameter(p1, p2, theta_rad):
    return abs( distance_between_points(p1, p2) / math.sin(theta_rad) )

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

def angle_of_vector_between_points_360_rad(p1,p2):
    return angle_of_vector_360_rad((p1, p2))

def point_with_angle_and_distance_from_point(point, angle_rad, d):
    return (point[0] + d * math.cos(angle_rad), (point[1] + d * math.sin(angle_rad)))

def distance_between_points(p1, p2):
    return math.sqrt( (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 )