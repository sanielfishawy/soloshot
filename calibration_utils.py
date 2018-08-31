from sympy import symbols, tan, atan, solve
import math as math

def minimum_uncalibrated_distance(max_base_gps_error_radius, 
                                  max_compas_error_deg, 
                                  field_of_view_deg, 
                                  max_desired_offset_of_target_as_fraction_of_the_frame):

    # - Minimum raw trackable distance calculation
    # - For: 
    #    - No correction 
    #    - Using: 
    #        - raw base GPS
    #        - raw compass 
    #        - tag GPS
    #        - maximum field of view
    # - Given:
    #    - Maximum base gps error radius
    #    - Maximum compass error
    # - Determine:
    #    - Minimum caculated distance from tag to base using raw GPS
    # - Such that:
    #    - Tag will be within the middle P fraction of the frame. (i.e. 2/3 of the frame horizontally <1/6 reserve 
    #      on either side>)
    #    - When we first attempt to center the tag prior to calibration.
    #
    #
    #        R
    #    +--------+
    #    | *      |
    #    |    *   |
    #    |  *  *  *
    #    |        |  *
    #    | r * e  |*    *
    #    |        |        *
    #    |    *   |   *       *
    #  d |        |              *
    #    |     *  |      *          *
    #    |        |                    *
    #    |      * |         *             *
    #    |        |                          *
    #    |       *|            *                *
    #    |        |                                *
    #    +--------*---------------*-------------------*
    #
    #    |<--     P * I/2      -->|    
    #    |<--                I/2                   -->|  


    R, d, e, F, I, P = symbols("R d e F I P")       
    R = max_base_gps_error_radius
    e = max_compas_error_deg
    F = field_of_view_deg
    P = max_desired_offset_of_target_as_fraction_of_the_frame

    equation = tan( atan(R/d) + e ) - P*tan(F/2)

    return solve(equation, d)
    