import math

#                    C    0    D
#                    .          .
#                 .                 .
#             B .                     . E
#             A .                     . F
#                 .                 .
#                    .          .
#                  H   180 | -180  G
#
# Signs are defined to be compatible VisualAngleCalculator so that we can simply
# add subtended motor angles to subtended visual angles to get subtended angle
# of a moving subject.
#
# VisualAngleCalculator defines movement from left to right across the screen to be
# a positive angle.
#
# Therefore:
#   - clockwise motor motion ABCDEFGH should give positive angles.
#   - counter clockwise motor motion HGFEDCBA should give negative angles.
#
# Motor is assumed to have moved through the acute angle (< pi) rather than the
# obtuse angle (> pi) in order to determine whether motion is clockwise or counterclockwise.
#
#    Early(e)     Late(l)     Expected_sign     Algorithm
#    --------     -------     -------------     ---------
#       A            B             +              e - l         (0 < e-l < pi)
#       C            D             +              e - l         (0 < e-l < pi)
#       E            F             +              e - l         (0 < e-l < pi)
#
#       B            A             -              e - l         (-pi < e-l < 0)
#       D            C             -              e - l         (-pi < e-l < 0)
#       F            E             -              e - l         (-pi < e-l < 0)
#
#       G            H             +              e - l + 2pi   (-2pi < e-l < -pi)
#       H            G             -              e - l - 2pi   (  pi < e-l < 2pi)
#
#       A            F             -              e - l - 2pi   (  pi < e-l < 2pi)

def get_acute_subtened_motor_angle_rad(early_angle_rad, late_angle_rad):
    r = early_angle_rad - late_angle_rad
    if r < - math.pi:
        r = r + (2 *  math.pi)
    if r >  math.pi:
        r = r - (2 *  math.pi)
    return r
