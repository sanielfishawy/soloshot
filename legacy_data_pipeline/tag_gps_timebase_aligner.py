# pylint: disable=C0413, C0301
import sys
import os
from pathlib import Path
import numpy as np
import numpy_extensions.numpy_ndarray_extensions # pylint: disable=W0611

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper as LDFH
from legacy_data_pipeline.calibration_data_filer import CalibrationDataFiler
from tk_canvas_renderers.tag_gps_timebase_aligner_ui import TagGpsTimebaseAlignerUi
from tk_canvas_renderers.geo_map_scrubber import GeoMapScrubber

class TagGpsTimebaseAligner:
    '''Determines with user assistance statistics for offset in
       time between tag_gps timebase and video time'''

    IFV = 'ifv'
    TAG_IDX = 'tag_idx'
    TAG_TIME = 'tag_time'

    AGGREGATE_RESULTS = 'aggregate_results'
    ALIGNMENT_STATS = 'alignment_stats'
    DELAY_VIDEO_TO_TAG_GPS = 'delay_video_to_tag_gps'

    MAX = 'max'
    MEAN = 'mean'
    MIN = 'min'
    NUM = 'num'

    INDIVIDUAL_RESULTS = 'individual_results'

    TAG_DATA = 'tag_data'
    TAG_IDX = 'tag_idx'
    TAG_TIME = 'tag_time'

    VIDEO_DATA = 'video_data'
    FRAME_NUM = 'frame_num'
    TIME_MS = 'time_ms'
    VIDEO_ID = 'video_id'
    VIDEO_URL = 'video_url'

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

        # helpers
        self._ldfh = LDFH(self._input_data_head_path)
        self._calibration_data_filer = CalibrationDataFiler(self._results_head_path)

        # state
        self._alignment_data = []

        # lazy inits
        self._latitude_series = None
        self._longitude_series = None
        self._time_series = None

    def _display_ui(self):
        geo_map_scrubber = GeoMapScrubber(
            latitude_series=self._get_latitude_series(),
            longitude_series=self._get_longitude_series(),
            time_series=self._get_time_series(),
        )
        TagGpsTimebaseAlignerUi(
            geo_map_scrubber=geo_map_scrubber,
            video_path=self._get_video_path(),
            save_alignment_callback=self._save_alignment_callback,
            done_callback=self._done_callback,
        ).run()

    def _save_alignment_callback(self, image_from_video, tag_idx, tag_time):
        self._alignment_data.append(
            {
                self.__class__.IFV: image_from_video,
                self.__class__.TAG_IDX: tag_idx,
                self.__class__.TAG_TIME: tag_time,
            }
        )
        print('Saved alignment delay: ', self._get_delay_video_to_tag(self._alignment_data[-1]))

    def _done_callback(self):
        self._calibration_data_filer.save_as_yml(
            obj=self._get_stats(),
            data_dir_name=self._session_dir,
            calibration_file=CalibrationDataFiler.TAG_GPS_TIMEBASE_ALIGNMENT,
        )

    def _get_stats(self):
        return {
            self.__class__.AGGREGATE_RESULTS: self._get_aggregate_stats(),
            self.__class__.INDIVIDUAL_RESULTS: self._get_individual_stats_list(),
        }

    def _get_aggregate_stats(self):
        delays = [stat[self.__class__.DELAY_VIDEO_TO_TAG_GPS]
                  for stat in self._get_individual_stats_list()]
        delays = np.array(delays)
        return {
            self.__class__.DELAY_VIDEO_TO_TAG_GPS:
                {
                    self.__class__.MEAN: int(round(np.mean(delays))),
                    self.__class__.MAX: int(round(np.max(delays))),
                    self.__class__.MIN: int(round(np.min(delays))),
                }
        }

    def _get_individual_stats_list(self):
        r = []
        for datum in self._alignment_data:
            r.append(
                {
                    self.__class__.TAG_DATA:
                        {
                            self.__class__.TAG_IDX: int(datum[self.__class__.TAG_IDX]),
                            self.__class__.TAG_TIME: int(datum[self.__class__.TAG_TIME]),
                        },
                    self.__class__.VIDEO_DATA: datum[self.__class__.IFV].get_as_dict(),
                    self.__class__.DELAY_VIDEO_TO_TAG_GPS: self._get_delay_video_to_tag(datum),
                }
            )
        return r

    def _get_delay_video_to_tag(self, datum):
        video_time = datum[self.__class__.IFV].get_time_ms()
        return int(datum[self.__class__.TAG_TIME] - video_time)

    def _get_latitude_series(self):
        if self._latitude_series is None:
            self._latitude_series =\
                self._ldfh.get_field_from_npz_file(self._session_dir,
                                                   LDFH.TAG_NPZ_FILE,
                                                   LDFH.TAG_LATITUDE_FIELD,
                                                  )
        return self._latitude_series

    def _get_longitude_series(self):
        if self._longitude_series is None:
            self._longitude_series =\
                self._ldfh.get_field_from_npz_file(self._session_dir,
                                                   LDFH.TAG_NPZ_FILE,
                                                   LDFH.TAG_LONGITUDE_FIELD,
                                                  )
        return self._longitude_series

    def _get_time_series(self):
        if self._time_series is None:
            self._time_series =\
                self._ldfh.get_field_from_npz_file(self._session_dir,
                                                   LDFH.TAG_NPZ_FILE,
                                                   LDFH.TAG_TIME_FIELD,
                                                  )
        return self._time_series

    def _get_video_path(self):
        return self._ldfh.get_video_path(self._session_dir)
