# pylint: disable=C0413, W0611
import sys
import os
import numpy as np

sys.path.insert(0, os.getcwd())
import numpy_extensions.numpy_ndarray_extensions

class StableFovSegmenter:
    '''
    Based on fov_timebase_alignment.yml we see that start of Fov transitions
    in normalized Fov time align variably with the video from. With a delay
    of fov_to_video of between -700 ms to +300 ms. Moreover Fov transitions
    occur over a time of as much as 2.3 seconds.

    In order to perform calibration and other measurements on the data we should
    mask out these potential FOV transition times.

    This tool takes Fov and Fov time. And returns a list of start and stop times in
    Fov time where Fov is certain to be stable and have settled.

    Segments in video_time with these same start and stop times should have unchanging
    Fov with wide enough guardbands i.e. 3000 ms before and 3000 ms after a transition.
    '''

    FOV = 'fov'
    START_TRANSITION_FOV_IDX = 'start_transition_fov_idx'
    END_TRANSITION_FOV_IDX = 'end_transition_fov_idx'
    START_GUARDED_FOV_TIME = 'start_guarded_fov_time'
    END_GUARDED_FOV_TIME = 'end_guarded_fov_time'
    TOO_SHORT = 'too_short'

    def __init__(
            self,
            fov_series: np.ndarray,
            fov_time_series: np.ndarray,
            guard_band_before_transition_ms: int = 3000,
            guard_band_after_transition_ms: int = 3000,
    ):
        self._fov_series = fov_series
        self._fov_time_series = fov_time_series
        self._guard_band_before_transition_ms = guard_band_before_transition_ms
        self._guard_band_after_transition_ms = guard_band_after_transition_ms

        # lazy init
        self._normalized_fov_time_series = None
        self._transitions = None

    def get_stable_segments(self):
        r = []
        start_idx = 0
        for transition in self._get_transitions():
            r.append(self._get_stable_segment(start_idx, transition))
            start_idx = transition

        last_transition = self._get_transitions()[-1]
        r.append(self._get_stable_segment(last_transition, self._fov_series.size - 1))

        return r

    @classmethod
    def segment_is_too_short(cls, segment):
        return segment[cls.TOO_SHORT]

    def _get_stable_segment(self, start_idx, end_idx):
        start_guarded_time = self._get_guarded_fov_time_after_idx(start_idx)
        end_guarded_time = self._get_guarded_fov_time_before_idx(end_idx)
        return {
            self.__class__.FOV: self._get_stable_fov(start_idx),
            self.__class__.START_TRANSITION_FOV_IDX: start_idx,
            self.__class__.END_TRANSITION_FOV_IDX: end_idx,
            self.__class__.START_GUARDED_FOV_TIME: start_guarded_time,
            self.__class__.END_GUARDED_FOV_TIME: end_guarded_time,
            self.__class__.TOO_SHORT: self._get_segment_is_too_short(
                start_guarded_time=start_guarded_time,
                end_guarded_time=end_guarded_time,
            )
        }

    def _get_stable_fov(self, start_idx):
        stable_idx = min(self._fov_series.size - 1, start_idx + 1)
        return self._fov_series[stable_idx]

    def _get_segment_is_too_short(self, start_guarded_time, end_guarded_time):
        return start_guarded_time >= end_guarded_time

    def _get_transitions(self):
        if self._transitions is None:
            self._transitions = self._fov_series.transitions()
        return self._transitions

    def _get_normalized_fov_time_series(self):
        if self._normalized_fov_time_series is None:
            self._normalized_fov_time_series = self._fov_time_series - self._fov_time_series[0]
        return self._normalized_fov_time_series


    def _get_guarded_fov_time_before_idx(self, idx):
        return max(
            0,
            self._get_normalized_fov_time_series()[idx] - self._guard_band_before_transition_ms
        )

    def _get_guarded_fov_time_after_idx(self, idx):
        return min(
            self._get_normalized_fov_time_series()[-1],
            self._get_normalized_fov_time_series()[idx] + self._guard_band_after_transition_ms
        )
