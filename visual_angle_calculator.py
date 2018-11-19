import math

#       |------------x1----------0----------------------x2-|
#                     .          |                    .
#                      .         |                  .
#                       .        | d              .
#                        .       |              .
#                         .      |            .
#                          .     |          .
#                           .    |        .
#                            . a1|  a2  .
#                             .  |    .
#                              . |  .
#                               .|.
#                                c
#
#
# Moving from left to right gives postive subtended angles
# Moving from right to left gives negative subtended angles
# x1 is assumed to come before x2 in time.
# x from image generator may be positive (right of center screen) e.g. x2
# or negative (left of center screen) e.g. x1
#

def get_subtended_angle_with_x_rad(x_1, x_2, image_width, fov_rad):
    a_1 = get_angle_relative_to_center_with_x_rad(x_1, image_width, fov_rad)
    a_2 = get_angle_relative_to_center_with_x_rad(x_2, image_width, fov_rad)
    return a_2 - a_1

def get_angle_relative_to_center_with_x_rad(x_pos, image_width, fov_rad):
    return math.atan2(x_pos, get_d(image_width, fov_rad))

def get_d(image_width, fov_rad):
    return image_width / 2 / math.tan(fov_rad / 2)
