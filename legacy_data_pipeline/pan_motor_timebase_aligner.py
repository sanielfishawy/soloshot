# pylint: disable=C0413
import sys
import os
from pathlib import Path
from typing import List
import numpy as np
import matplotlib.pyplot as plt
import numpy_extensions.numpy_ndarray_extensions # pylint: disable=W0611

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper as LDFH
from legacy_data_pipeline.calibration_data_filer import CalibrationDataFiler
from video_and_photo_tools.image_from_video_grabber import ImageFromVideoGrabber
from video_and_photo_tools.image_from_video import ImageFromVideo
from tk_canvas_renderers.scrub_picker import ScrubPicker

class PanMotorTimeBaseAligner:
    '''Determines with user assistance via scrubber picker statistics for offset in
       time between pan_motor_read timebase and video time'''

    RAW_RESULTS = 'raw_results'
    AGGREGATE_RESULTS = 'aggregate_results'

    MIN_OR_MAX = 'min_or_max'
    MIN = 'min'
    MAX = 'max'
    MEAN = 'mean'
    N = 'n'
    DATA = 'data'

    DELAY_MOTOR_TO_VIDEO = 'delay_motor_to_video'

    BASE_TIME = 'base_time'

    PAN_LOCAL_MINIMA = 'pan_local_minima'
    PAN_LOCAL_MAXIMA = 'pan_local_maxima'
    PAN_COMBINED = 'pan_combined'



    def __init__(self,
                 session_dir: str,
                 input_data_head_path=Path('/Volumes/WD'),
                 results_head_path=Path('.')  / 'data/calibration_data',
                 cache_dir_path=Path('/Volumes/WD/image_cache'),
                 num_points=6,
                ):
        self._session_dir = session_dir
        self._input_data_head_path = input_data_head_path
        self._results_head_path = results_head_path
        self._cache_dir_path = cache_dir_path
        self._num_points = num_points

        self._ldfh = LDFH(self._input_data_head_path)
        self._calibration_data_filer = CalibrationDataFiler(self._results_head_path)

        self.maxima_text_color = 'red'
        self.minima_text_color = 'green'
        self.fontsize = 8

        # Lazy initializers
        self.pan_motor_read_data = None
        self.base_time = None
        self.motor_local_maxima = None
        self.motor_local_minima = None

        # State
        self._base_time = None
        self._min_or_max = None
        self._alignment_results = []

    def visualize_motor_local_maxima_and_minima(self):
        fig, axis = plt.subplots() # pylint: disable=W0612
        axis.plot(self.get_normalized_base_time(), self.get_motor_data())

        # maxima_shoulder_steepness = [self.get_motor_data().get_shoulder_steepness_around_idx(maximum, 4)
        #                              for maximum in self.get_motor_maxima()]

        for idx, val in enumerate(self.get_motor_values_at_maxima()):
            axis.text(self.get_normalized_base_time()[self.get_motor_maxima()[idx]],
                      val,
                      str(idx),
                      color=self.maxima_text_color,
                      fontsize=self.fontsize,
                      )

        for idx, val in enumerate(self.get_motor_values_at_minima()):
            axis.text(self.get_normalized_base_time()[self.get_motor_minima()[idx]],
                      val,
                      str(idx),
                      color=self.minima_text_color,
                      fontsize=self.fontsize,
                      )

        plt.show()

    def get_motor_maxima(self):
        if self.motor_local_maxima is None:
            self.motor_local_maxima = self.get_motor_data().\
                                           local_maxima_sorted_by_peakyness_and_monotonic_with_steep_shoulders(8, 4, 2) # pylint: disable=C0301
        return self.motor_local_maxima[:self._num_points]

    def get_motor_values_at_maxima(self):
        return np.array([self.get_motor_data()[idx] for idx in self.get_motor_maxima()])

    def get_time_at_maxima(self):
        return np.array([self.get_normalized_base_time()[maximum]
                         for maximum in self.get_motor_maxima()])

    def get_motor_minima(self):
        if self.motor_local_minima is None:
            self.motor_local_minima = self.get_motor_data().\
                                           local_minima_sorted_by_peakyness_and_monotonic_with_steep_shoulders(8, 4, 2) # pylint: disable=C0301
        return self.motor_local_minima[:self._num_points]

    def get_motor_values_at_minima(self):
        return np.array([self.get_motor_data()[idx] for idx in self.get_motor_minima()])

    def get_time_at_minima(self):
        return np.array([self.get_normalized_base_time()[minimum]
                         for minimum in self.get_motor_minima()])

    def show_scrub_picker_for_maxima(self):
        self._min_or_max = self.__class__.MAX
        for time in self.get_time_at_maxima():
            self._base_time = time
            self.show_scrub_picker_for_time(time)

    def show_scrub_picker_for_minima(self):
        self._min_or_max = self.__class__.MIN
        for time in self.get_time_at_minima():
            self._base_time = time
            self.show_scrub_picker_for_time(time)

    def show_scrub_picker_for_min_and_max(self):
        self.show_scrub_picker_for_minima()
        self.show_scrub_picker_for_maxima()

    def show_scrub_picker_for_time(self, time):
        ScrubPicker(images_from_video=self.get_images_around_time(time),
                    selector_type=ScrubPicker.SELECT_SINGLE_IMAGE,
                    callback=self._scrubber_callback,
                    ).run()


    def get_images_around_time(self, time):
        return self.get_ifv_grabber().get_images_around_time_ms(time, before=40, after=40)

    def get_motor_data(self) -> np.ndarray:
        if self.pan_motor_read_data is None:
            self.pan_motor_read_data = self._ldfh.get_field_from_npz_file(self._session_dir,
                                                                          LDFH.BASE_NPZ_FILE,
                                                                          LDFH.PAN_MOTOR_READ_FIELD,
                                                                          )
        return self.pan_motor_read_data

    def get_base_time(self):
        if self.base_time is None:
            self.base_time = self._ldfh.get_field_from_npz_file(self._session_dir,
                                                                LDFH.BASE_NPZ_FILE,
                                                                LDFH.BASE_TIME_FIELD,
                                                               )
        return self.base_time

    def get_normalized_base_time(self):
        return self.get_base_time() - self.get_base_time()[0]

    def get_motor_data_time_tuples(self):
        return np.dstack((self.get_normalized_base_time(), self.get_motor_data()))[0]

    def get_video_path(self):
        return self._ldfh.get_video_path(self._session_dir)

    def get_ifv_grabber(self) -> ImageFromVideoGrabber:
        return ImageFromVideoGrabber(self.get_video_path(),
                                     cache_dir_path=self._cache_dir_path)

    def _scrubber_callback(self, images_from_video: List[ImageFromVideo]):
        ifv = images_from_video[0]
        r = ifv.get_as_dict()
        r[self.__class__.MIN_OR_MAX] = self._min_or_max
        r[self.__class__.BASE_TIME] = int(self._base_time)
        r[self.__class__.DELAY_MOTOR_TO_VIDEO] = ifv.get_time_ms() - int(self._base_time)
        self._alignment_results.append(r)

    def _get_aggregate_data(self):
        r = {}
        local_min_data = np.array([])
        local_max_data = np.array([])
        for result in self._alignment_results:
            if result[self.__class__.MIN_OR_MAX] == self.__class__.MIN:
                local_min_data = np.append(local_min_data,
                                           result[self.__class__.DELAY_MOTOR_TO_VIDEO])
            else:
                local_max_data = np.append(local_max_data,
                                           result[self.__class__.DELAY_MOTOR_TO_VIDEO])
        combined_data = np.concatenate((local_min_data, local_max_data))

        r[self.__class__.PAN_LOCAL_MINIMA] = self._get_stats_from_data(local_min_data)
        r[self.__class__.PAN_LOCAL_MAXIMA] = self._get_stats_from_data(local_max_data)
        r[self.__class__.PAN_COMBINED] = self._get_stats_from_data(combined_data)
        return r

    def _get_stats_from_data(self, data: np.ndarray):
        r = {}
        r[self.__class__.N] = int(data.size)
        r[self.__class__.DATA] = data.tolist()
        r[self.__class__.MIN] = int(np.min(data))
        r[self.__class__.MAX] = int(np.max(data))
        r[self.__class__.MEAN] = int(np.mean(data))
        return r

    def _get_results_object(self):
        r = {}
        r[self.__class__.RAW_RESULTS] = self._alignment_results
        r[self.__class__.AGGREGATE_RESULTS] = self._get_aggregate_data()
        return r

    def log_data(self):
        self._calibration_data_filer.save_as_yml(self._get_results_object(),
                                                 self._session_dir,
                                                 CalibrationDataFiler.PAN_MOTOR_TIMEBASE_ALIGNMENT,
                                                )

    def run(self):
        self.show_scrub_picker_for_min_and_max()
        self.log_data()