# pylint: disable=C0413, W0212
import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.tag_gps_timebase_aligner import TagGpsTimebaseAligner

class TestTagGpsTimebaseAligner(unittest.TestCase):

    def setUp(self):
        self.session_dir = 'Aug_17_Palo_Alto_High_2nd_time_B80_ottofillmore'

    def run(self):
        TagGpsTimebaseAligner(
            session_dir=self.session_dir,
        )._display_ui()

    def dont_calculate_aggregate_stats(self):
        delays = np.array([ -523, 325, -539, 82, -386, -90, -721, -494, -520, 192, 223, 145, -98, 132, -51, 215, -31, 187, -66, 99, 147, -177, 171, -60, 131, 217])
        mean = np.mean(delays)
        maximum = np.max(delays)
        minimum = np.min(delays)
        print ('mean', mean, 'max', maximum, 'min', minimum)

        delays = np.array([156, -911, 172, -564])
        mean = np.mean(delays)
        maximum = np.max(delays)
        minimum = np.min(delays)
        print ('mean', mean, 'max', maximum, 'min', minimum)


if __name__ == '__main__':
    unittest.main()
