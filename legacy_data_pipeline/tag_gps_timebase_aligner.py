# pylint: disable=C0413, C0301
import sys
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import numpy_extensions.numpy_ndarray_extensions # pylint: disable=W0611

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper as LDFH
from legacy_data_pipeline.calibration_data_filer import CalibrationDataFiler
from video_and_photo_tools.image_from_video_grabber import ImageFromVideoGrabber
from video_and_photo_tools.image_from_video import ImageFromVideo
from tk_canvas_renderers.scrub_picker import ScrubPicker

class TagGpsTimebaseAligner:
    '''Determines with user assistance statistics for offset in
       time between tag_gps timebase and video time'''

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

        # lazy inits
        self._latitude_series = None
        self._longitude_series = None

    def get_latitude_series(self):
        if self._latitude_series is None:
            self._latitude_series =\
                self._ldfh.get_field_from_npz_file(self._session_dir,
                                                   LDFH.TAG_NPZ_FILE,
                                                   LDFH.TAG_LATITUDE_FIELD,
                                                  )
        return self._latitude_series

    def get_longitude_series(self):
        if self._longitude_series is None:
            self._longitude_series =\
                self._ldfh.get_field_from_npz_file(self._session_dir,
                                                   LDFH.TAG_NPZ_FILE,
                                                   LDFH.TAG_LONGITUDE_FIELD,
                                                  )
        return self._longitude_series

    def _get_first_lat_long(self):
        return (
            self.get_latitude_series()[100],
            self.get_longitude_series()[100]
        )
