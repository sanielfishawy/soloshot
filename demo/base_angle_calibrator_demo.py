import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
from tests.test_base_angle_calibrator import TestBaseAngleCalibrator

TestBaseAngleCalibrator().setUp(tag_gps_angle_threshold=6, compass_err_deg=10).visualize()