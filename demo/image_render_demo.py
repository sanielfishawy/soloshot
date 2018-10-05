import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
from tests.test_image_renderer import TestImageRenderer

TestImageRenderer().setUp(num_randomly_moving_objects=0).visualize()