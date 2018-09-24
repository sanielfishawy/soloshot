import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
from tests.test_base_position_calibrator import TestBasePositionCalibrator

TestBasePositionCalibrator().setUp(num_randomly_moving_objects=30, tag_gps_angle_threshold=10).visualize()