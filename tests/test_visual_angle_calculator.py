# pylint: disable=C0413
import sys
import os
import unittest
import math

sys.path.insert(0, os.getcwd())
import visual_angle_calculator as Vac

class TestVisualAngleCalculator(unittest.TestCase):

    def setUp(self):
        pass

    def test(self):
        fov = math.pi / 4
        image_width = 100

        angle_to_center = Vac.get_angle_relative_to_center_with_x_rad(
            x_pos=image_width/2,
            fov_rad=fov,
            image_width=image_width,
        )
        self.assertAlmostEqual(angle_to_center, fov/2)



if __name__ == '__main__':
    unittest.main()