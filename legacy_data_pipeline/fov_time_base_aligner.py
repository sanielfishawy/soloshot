# pylint: disable=C0413, C0301
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


class FovTimebaseAligner:
    '''Determines with user assistance via scrubber picker statistics for offset in
       time between fov timebase and video time'''

    AGGREGATE_RESULTS = 'aggregate_results'
    UNIQUE_FOVS = 'unique_fovs'
    UNIQUE_TRANSITIONS = 'unique_transitions'

    INDIVIDUAL_RESULTS = 'individual_results'

    FOV_DATA = 'fov_data'
    TRANSITION_LEVELS = 'transition_levels'
    TRANSITION_INDEX = 'transition_index'
    TRANSITION_TIME = 'transition_time'

    BEGIN = 'begin'
    END = 'end'

    ZOOM_IN = 'zoom_in'
    ZOOM_OUT = 'zoom_out'

    VIDEO_DATA = 'video_data'
    FRAME_NUM = 'frame_num'
    TIME_MS = 'time_ms'
    DURATION = 'duration'
    FRAMES = 'frames'

    ALIGNMENT = 'alignment'
    DELAY_FOV_TO_VIDEO = 'delay_fov_to_video'

    ALIGNMENT_STATS = 'alignment_stats'
    MIN_DELAY = 'min_delay'
    MAX_DELAY = 'max_delay'
    MEAN_DELAY = 'mean_delay'
    MIN_DURATION = 'min_duration'
    MAX_DURATION = 'max_duration'
    MEAN_DURATION = 'mean_duration'


    def __init__(self,
                 session_dir: str,
                 input_data_head_path=Path('/Volumes/WD'),
                 results_head_path=Path('.')  / 'data/calibration_data',
                 cache_dir_path=Path('/Volumes/WD/image_cache'),
                ):
        self._session_dir = session_dir
        self._input_data_head_path = input_data_head_path
        self._results_head_path = results_head_path
        self._cache_dir_path = cache_dir_path

        # settings
        self._anotation_color = 'green'
        self._anotation_fontsize = '8'

        self._ldfh = LDFH(self._input_data_head_path)
        self._calibration_data_filer = CalibrationDataFiler(self._results_head_path)

        # lazy inits
        self._fov_time_series = None
        self._fov_data_series = None
        self._unique_fovs = None
        self._transition_indexes = None
        self._transition_levels = None
        self._unique_transitions = None

        # state
        self._alignment_results = {}
        self._alignment_stats_delays = []
        self._alignment_stats_durations = []
        self._current_transition = None

    def visualize(self):
        fig, axis = plt.subplots() # pylint: disable=W0612
        axis.plot(self.get_normalized_fov_time(), self.get_fov_data_series())

        for key, hsh in self.get_unique_transitions().items():
            axis.text(self.get_normalized_fov_time()[hsh[self.__class__.TRANSITION_INDEX]],
                      hsh[self.__class__.TRANSITION_LEVELS][0],
                      key,
                      color=self._anotation_color,
                      fontsize=self._anotation_fontsize,
                      )

        plt.show()

    def get_fov_time_series(self):
        if self._fov_time_series is None:
            self._fov_time_series =\
                self._ldfh.get_field_from_npz_file(self._session_dir,
                                                   LDFH.LENS_NPZ_FILE,
                                                   LDFH.LENS_TIME_FIELD,
                                                  )
        return self._fov_time_series

    def get_fov_data_series(self):
        if self._fov_data_series is None:
            self._fov_data_series =\
                self._ldfh.get_field_from_npz_file(self._session_dir,
                                                   LDFH.LENS_NPZ_FILE,
                                                   LDFH.LENS_FOV_FIELD,
                                                  )
        return self._fov_data_series

    def get_normalized_fov_time(self):
        return self.get_fov_time_series() - self.get_fov_data_series()[0]

    def get_unique_fovs(self):
        if self._unique_fovs is None:
            self._unique_fovs = np.unique(self.get_fov_data_series())
        return self._unique_fovs

    def get_fov_transition_indexes(self):
        if self._transition_indexes is None:
            self._transition_indexes = self.get_fov_data_series().transitions()
        return self._transition_indexes[:2]

    def get_fov_transition_levels(self):
        if self._transition_levels is None:
            self._transition_levels =\
                self.get_fov_data_series().levels_around_transitions(self.get_fov_transition_indexes())
        return self._transition_levels

    def get_unique_transitions(self):
        if self._unique_transitions is None:
            r = {}
            for idx, transition_index in enumerate(self.get_fov_transition_indexes()):
                transition_levels = self.get_fov_transition_levels()[idx]

                if str(transition_levels) in r:
                    continue

                r[str(transition_levels)] = {
                    self.__class__.TRANSITION_LEVELS: transition_levels,
                    self.__class__.TRANSITION_INDEX: transition_index,
                    self.__class__.TRANSITION_TIME: self.get_fov_time_series()[transition_index],
                }

            self._unique_transitions = r
        return self._unique_transitions

    def show_scrub_picker_for_transitions(self):
        for _, transition in self.get_unique_transitions().items():
            self._current_transition = transition
            self.show_scrub_picker_for_time(transition[self.__class__.TRANSITION_INDEX],
                                            transition[self.__class__.TRANSITION_TIME])

    def show_scrub_picker_for_time(self, idx, time):
        ScrubPicker(images_from_video=self.get_images_around_time(time),
                    selector_type=ScrubPicker.SELECT_RANGE,
                    callback=self._scrubber_callback,
                    selected_start_frame_num=None,
                    ).run()

    def get_images_around_time(self, time):
        return self.get_ifv_grabber().get_images_around_time_ms(time, before=50, after=80)

    def get_ifv_grabber(self) -> ImageFromVideoGrabber:
        return ImageFromVideoGrabber(self.get_video_path(),
                                     cache_dir_path=self._cache_dir_path)

    def get_video_path(self):
        return self._ldfh.get_video_path(self._session_dir)

    def _get_aggregate_data(self):
        r = {
            self.__class__.UNIQUE_FOVS: self.get_unique_fovs().tolist(),
            self.__class__.UNIQUE_TRANSITIONS:
                [self._get_name_for_transition(transition)
                 for _, transition in self.get_unique_transitions().items()],
            self.__class__.ALIGNMENT_STATS: self._get_alignment_stats(),
        }
        return r

    def _get_alignment_stats(self):
        return {
            self.__class__.MIN_DELAY: int(np.min(np.array(self._alignment_stats_delays))),
            self.__class__.MAX_DELAY: int(np.max(np.array(self._alignment_stats_delays))),
            self.__class__.MEAN_DELAY: int(np.mean(np.array(self._alignment_stats_delays))),

            self.__class__.MIN_DURATION: int(np.min(np.array(self._alignment_stats_durations))),
            self.__class__.MAX_DURATION: int(np.max(np.array(self._alignment_stats_durations))),
            self.__class__.MEAN_DURATION: int(np.mean(np.array(self._alignment_stats_durations))),
        }

    def _get_results_object(self):
        r = {}
        r[self.__class__.AGGREGATE_RESULTS] = self._get_aggregate_data()
        r[self.__class__.INDIVIDUAL_RESULTS] = self._alignment_results
        return r

    def save_results(self):
        self._calibration_data_filer.save_as_yml(self._get_results_object(),
                                                 self._session_dir,
                                                 CalibrationDataFiler.FOV_TIMEBASE_ALIGNMENT,
                                                )

    def _scrubber_callback(self, selection: list):
        delay_fov_to_video = \
            int(selection[0].get_time_ms() - self._current_transition[self.__class__.TRANSITION_TIME]),

        duration = self._get_duration_ms(selection[0], selection[1])

        r = {
            self.__class__.VIDEO_DATA: {
                self.__class__.BEGIN: self._get_ifv_info(selection[0]),
                self.__class__.END: self._get_ifv_info(selection[1]),
                self.__class__.DURATION: {
                    self.__class__.TIME_MS: duration,
                    self.__class__.FRAMES: self._get_duration_frames(selection[0], selection[1]),
                },
            },
            self.__class__.FOV_DATA: {
                self.__class__.TRANSITION_INDEX: int(self._current_transition[self.__class__.TRANSITION_INDEX]),
                self.__class__.TRANSITION_TIME: int(self._current_transition[self.__class__.TRANSITION_TIME]),
            },
            self.__class__.ALIGNMENT: {
                self.__class__.DELAY_FOV_TO_VIDEO: delay_fov_to_video,
            },
        }
        self._alignment_results[self._get_name_for_transition(self._current_transition)] = r
        self._alignment_stats_delays.append(delay_fov_to_video)
        self._alignment_stats_durations.append(duration)

    def _get_ifv_info(self, ivf):
        return {
            self.__class__.FRAME_NUM: ivf.get_frame_num(),
            self.__class__.TIME_MS: ivf.get_time_ms(),
        }

    def _get_duration_ms(self, begin_ifv: ImageFromVideo, end_ifv: ImageFromVideo):
        return end_ifv.get_time_ms() - begin_ifv.get_time_ms()

    def _get_duration_frames(self, begin_ifv: ImageFromVideo, end_ifv: ImageFromVideo):
        return end_ifv.get_frame_num() - begin_ifv.get_frame_num()

    def _get_name_for_transition(self, transition):
        return (
            f'{self._get_zoom_type_for_transition(transition)}: '
            f'{str(transition[self.__class__.TRANSITION_LEVELS])}'
        )

    def _get_zoom_type_for_transition(self, transition: dict):
        if transition[self.__class__.TRANSITION_LEVELS][0] < transition[self.__class__.TRANSITION_LEVELS][1]:
            return self.__class__.ZOOM_OUT
        else:
            return self.__class__.ZOOM_IN

    def run(self):
        self.show_scrub_picker_for_transitions()
        self.save_results()
