import sys
from forbiddenfruit import curse
import numpy as np

def __ndarray_local_maxima(self):
    range_spread = 4
    approx_maxima = np.ediff1d(self).negative_zero_crossings()
    actual_maxima = []
    for approx in approx_maxima:
        idx_range = np.clip(np.array([approx-range_spread, approx+range_spread]),
                            0, self.size)
        actual_maxima.append(self.argmax_in_range(idx_range))
    return actual_maxima

def __ndarray_local_minima(self):
    range_spread = 4
    approx_minima = np.ediff1d(self).positive_zero_crossings()
    actual_minima = []
    for approx in approx_minima:
        idx_range = np.clip(np.array([approx-range_spread, approx+range_spread]),
                            0, self.size)
        actual_minima.append(self.argmin_in_range(idx_range))
    return actual_minima

def __ndarray_is_monotonic_around_peak_or_trough(self, idx, band):
    idx_range = np.clip(np.array([idx - band, idx + band]), 0, self.size)
    sign_diff = np.sign(np.diff(self[idx_range[0]: idx_range[1]]))
    sign_diff_no_zero = np.array([el for el in sign_diff if el != 0])
    diff_sign_diff = np.diff(sign_diff_no_zero)
    return len([el for el in diff_sign_diff if el != 0]) <= 1

def __ndarray_get_shoulder_steepness_around_idx(self, idx, band):
    dx1 = np.ediff1d(self)
    idx_range = np.clip(np.array([idx - band, idx + band]), 0, dx1.size)
    return np.take(dx1, idx_range)

def __ndarray_has_steep_shoulders_around_idx(self, idx, band, threshold):
    return np.all(np.abs(self.get_shoulder_steepness_around_idx(idx, band)) > threshold)

def __ndarray_local_maxima_sorted_by_peakyness(self):
    return self.sort_indexes_by_peakyness(self.local_maxima())

def __ndarray_local_minima_sorted_by_peakyness(self):
    return self.sort_indexes_by_peakyness(self.local_minima())

def __ndarray_local_maxima_sorted_by_peakyness_and_monotonic(self, band):
    maxima = self.local_maxima_sorted_by_peakyness()
    return np.array([maximum
                     for maximum in maxima
                     if self.is_monotonic_around_peak_or_trough(maximum, band)])

def __ndarray_local_minima_sorted_by_peakyness_and_monotonic(self, band):
    minima = self.local_minima_sorted_by_peakyness()
    return np.array([minimum
                     for minimum in minima
                     if self.is_monotonic_around_peak_or_trough(minimum, band)])

def __ndarray_local_maxima_sorted_by_peakyness_and_monotonic_with_steep_shoulders(self,
                                                                                  monotonic_band,
                                                                                  shoulder_band,
                                                                                  threshold
                                                                                  ):
    maxima = self.local_maxima_sorted_by_peakyness_and_monotonic(monotonic_band)
    return np.array([maximum
                     for maximum in maxima
                     if self.has_steep_shoulders_around_idx(maximum, shoulder_band, threshold)
                    ]
                   )

def __ndarray_local_minima_sorted_by_peakyness_and_monotonic_with_steep_shoulders(self,
                                                                                  monotonic_band,
                                                                                  shoulder_band,
                                                                                  threshold
                                                                                  ):
    minima = self.local_minima_sorted_by_peakyness_and_monotonic(monotonic_band)
    return np.array([minimum
                     for minimum in minima
                     if self.has_steep_shoulders_around_idx(minimum, shoulder_band, threshold)
                    ]
                   )

def __ndarray_zero_crossings(self):
    sign = np.sign(self)
    sign[sign == 0] = 1
    return np.where(np.diff(sign))[0]

def __ndarray_positive_zero_crossings(self):
    sign = np.sign(self)
    sign[sign == 0] = 1
    return np.where(np.diff(sign) > 0)[0]

def __ndarray_negative_zero_crossings(self):
    sign = np.sign(self)
    sign[sign == 0] = -1
    return np.where(np.diff(sign) < 0)[0]

def __ndarray_dx2(self):
    return np.ediff1d(np.ediff1d(self))

def __ndarray_argmax_in_range(self, idx_range: tuple):
    return np.argmax(self[idx_range[0]: idx_range[1]]) + idx_range[0]

def __ndarray_argmin_in_range(self, idx_range: tuple):
    return np.argmin(self[idx_range[0]: idx_range[1]]) + idx_range[0]

def __ndarray_peakyness_at_index(self, idx):
    dx2 = self.dx2()
    idx = np.clip(idx, 0, dx2.size)
    return np.abs(dx2[idx])

def __ndarray_sort_indexes_by_peakyness(self, indexes):
    idx_list = list(indexes)
    idx_list.sort(key=lambda idx: self.peakyness_at_index(idx))
    return np.flip(np.array(idx_list))

for method in [meth
               for meth in dir(sys.modules[__name__])
               if meth.startswith('__ndarray')]:

    user_friendly_name = method.replace('__ndarray_', '')
    curse(np.ndarray,
          user_friendly_name,
          getattr(sys.modules[__name__], method),
         )
