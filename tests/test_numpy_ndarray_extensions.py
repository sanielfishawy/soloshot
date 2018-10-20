# pylint: disable=C0413, W0611, C0103
import sys
import os
from pathlib import Path
import unittest
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.getcwd())
import numpy_extensions.numpy_ndarray_extensions

np.set_printoptions(threshold=np.inf)

class TestNumpyNdarrayExtensions(unittest.TestCase):

    def setUp(self):
        pass

    def visualize_local_maxima_on_motor_data(self):
        npz_path = Path('.') / 'data/test_data/test_npz/tag_toss_base.npz'
        npz_data = np.load(npz_path)
        motor_data = npz_data['pan_motor_read']
        maxima = motor_data.local_maxima_sorted_by_peakyness_and_monotonic(8)
        values_at_maxima = np.array([motor_data[idx] for idx in maxima])

        fig, ax = plt.subplots() # pylint: disable=W0612
        ax.plot(motor_data)

        for txt, val in enumerate(values_at_maxima):
            ax.annotate(str(txt), (maxima[txt], val))

        plt.show()

    def test_local_maxima_sorted_by_peakyness_and_monotonic_with_steep_shoulders(self):
        arr = np.sin(np.logspace(0, 20*np.pi, num=20*360, base=1.06))
        maxima = arr.\
                 local_maxima_sorted_by_peakyness_and_monotonic_with_steep_shoulders(8, 10, .001)

        self.assertEqual(maxima.size, 3)

    def test_has_steep_shoulders(self):
        arr = np.sin(np.logspace(0, 20*np.pi, num=20*360, base=1.06))
        maxima = arr.local_maxima_sorted_by_peakyness_and_monotonic(8)
        has_steep_shoulders = np.array([arr.has_steep_shoulders_around_idx(maximum, 10, .001)
                                        for maximum in maxima])
        np.testing.assert_array_equal(has_steep_shoulders,
                                      np.array([True, True, True, False, False, False]))

    def test_is_monotonic_around_peak_or_trough(self):
        up = np.arange(10)
        down = np.flip(np.arange(10))
        arr = np.concatenate((up, down, up, down, up))

        for center_point in [0, 10, 20, 30, 40, 50]:
            self.assertTrue(arr.is_monotonic_around_peak_or_trough(center_point, 5))

        for center_point in [10, 20, 30, 40]:
            self.assertFalse(arr.is_monotonic_around_peak_or_trough(center_point, 13))

    def test_peakyness_at_index(self):
        arr = np.sin(np.logspace(0, 20*np.pi, num=20*360, base=1.06))
        maxima = arr.local_maxima()
        peakyness = [arr.peakyness_at_index(idx) for idx in maxima]
        self.assertTrue(np.all(np.diff(peakyness) >= 0))

    def test_local_maxima_sorted_by_peakyness(self):
        arr = np.sin(np.logspace(0, 20*np.pi, num=20*360, base=1.06))
        sorted_local_maxima = arr.local_maxima_sorted_by_peakyness()
        self.assertTrue(np.all(np.diff(sorted_local_maxima) <= 0 ))

        arr = np.sin(np.flip(np.logspace(0, 20*np.pi, num=20*360, base=1.06)))
        sorted_local_maxima = arr.local_maxima_sorted_by_peakyness()
        self.assertTrue(np.all(np.diff(sorted_local_maxima) >= 0 ))

    def test_local_minima_sorted_by_peakyness(self):
        arr = np.sin(np.logspace(0, 20*np.pi, num=20*360, base=1.06))
        sorted_local_minima = arr.local_minima_sorted_by_peakyness()
        self.assertTrue(np.all(np.diff(sorted_local_minima) <= 0 ))

        arr = np.sin(np.flip(np.logspace(0, 20*np.pi, num=20*360, base=1.06)))
        sorted_local_minima = arr.local_minima_sorted_by_peakyness()
        self.assertTrue(np.all(np.diff(sorted_local_minima) >= 0 ))

    def test_local_maxima(self):
        arr = np.sin(np.linspace(0, 4*np.pi, 1440))
        np.testing.assert_array_equal(arr.local_maxima(), np.array([180, 899]))

    def test_local_minima(self):
        arr = np.sin(np.linspace(0, 4*np.pi, 1440))
        np.testing.assert_array_equal(arr.local_minima(), np.array([540, 1259]))

    def test_argmax_in_range(self):
        arr = np.arange(20)
        self.assertEqual(arr.argmax_in_range([3, 7]), 6)

    def test_zero_crossings(self):
        arr = np.array([-2, -1, 0, -1, 0, 1, 2, 1, 0, 1, 0, -1])
        exp = np.array([1, 2, 3, 10])
        np.testing.assert_array_equal(arr.zero_crossings(), exp)

        arr = np.array([2, 1, 0, 1, 0, -1, -2, -1, 0, -1, 0, 1])
        exp = [4, 7, 8, 9]
        np.testing.assert_array_equal(arr.zero_crossings(), exp)

    def test_positive_zero_crossings(self):
        arr = np.array([-2, -1, 0, -1, 0, 1, 2, 1, 0, 1, 0, -1])
        exp = [1, 3]
        np.testing.assert_array_equal(arr.positive_zero_crossings(), exp)

        arr = np.array([2, 1, 0, 1, 0, -1, -2, -1, 0, -1, 0, 1])
        exp = [7, 9]
        np.testing.assert_array_equal(arr.positive_zero_crossings(), exp)

    def test_negative_zero_crossings(self):
        arr = np.array([-2, -1, 0, -1, 0, 1, 2, 1, 0, 1, 0, -1])
        exp = [7, 9]
        np.testing.assert_array_equal(arr.negative_zero_crossings(), exp)

        arr = np.array([2, 1, 0, 1, 0, -1, -2, -1, 0, -1, 0, 1])
        exp = [1, 3]
        np.testing.assert_array_equal(arr.negative_zero_crossings(), exp)


if __name__ == '__main__':
    unittest.main()
