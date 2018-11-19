# pylint: disable=W0212, C0413
import sys
import os
import unittest

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.frame_rate_calculator import FrameRateCalculator

class TestFrameRateCalculator(unittest.TestCase):

    def setUp(self):
        self.frc = FrameRateCalculator()

    def dont_test_run(self):
        self.frc.run()

    def dont_test_setup_results_file(self):
        self.frc._setup_results_file()

    def dont_test_save_caclulated_results(self):
        self.frc._save_calculated_results()

    def dont_test_show_ifvs(self):
        self.frc._show_ifvs()

if __name__ == '__main__':
    unittest.main()
