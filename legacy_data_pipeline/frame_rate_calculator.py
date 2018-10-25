# pylint: disable=C0413, C0301
import os
import sys
from pathlib import Path

sys.path.insert(0, os.getcwd())
from video_and_photo_tools.image_from_video_grabber import ImageFromVideoGrabber
from tk_canvas_renderers.vertical_image_list import VerticalImageList
from legacy_data_pipeline.calibration_data_filer import CalibrationDataFiler

class FrameRateCalculator:
    '''Calculates the frame rate based on a video of a clock'''

    CLOCK_VIDEO_PATH = Path('/Volumes/WD/clock_video/SS3_VIDEO_2018_10_19_105439-1.MP4')
    # CLOCK_VIDEO_PAsTH = Path('/Volumes/WD/clock_video/clock_video.mp4')

    INPUT_DATA = 'input_data'
    START = 'start'
    END = 'end'
    HOURS = 'hours'
    MINUTES = 'minutes'
    SECONDS = 'seconds'

    CALCULATED_RESULTS = 'calculated_results'

    RESULTS_TEMPLATE = {
        INPUT_DATA: {
            START: {
                HOURS: None,
                MINUTES: None,
                SECONDS: None,
            },
            END: {
                HOURS: None,
                MINUTES: None,
                SECONDS: None,
            },
        },
        CALCULATED_RESULTS: None,
    }

    START_FRAME_NUM = 'start_frame_num'
    END_FRAME_NUM = 'end_frame_num'
    NUM_FRAMES = 'num_frames'
    START_TIME_MS = 'start_time_ms'
    END_TIME_MS = 'end_time_ms'
    TIME_DIFF = 'time_diff'
    FRAME_RATE = 'frame_rate'
    HEADER_FPS_CV2 = 'header_fps_cv2'
    VIDEO_ID = 'video_id'
    VIDEO_PATH = 'video_path'


    def __init__(self,
                 results_head_path=Path('./data/calibration_data'),
                 results_data_dir_name='frame_rate_calculation'
                ):
        assert self.__class__.CLOCK_VIDEO_PATH.resolve().is_file(), \
               f'No video found at {self.__class__.CLOCK_VIDEO_PATH.resolve}'

        self._results_head_path = results_head_path
        self._results_data_dir_name = results_data_dir_name

        self._ifvg = ImageFromVideoGrabber(self.__class__.CLOCK_VIDEO_PATH)
        self._cdf = CalibrationDataFiler(self._results_head_path)

        self._start_frame_num = 10

        # Lazy init
        self._results = None
        self._end_frame_num = None

    def _get_ifvs(self):
        r = [
            self._ifvg.get_image_at_frame_num(self._start_frame_num),
            self._ifvg.get_image_at_frame_num(self._get_end_frame_num())
        ]
        assert r[1].get_frame_num() == self._get_end_frame_num()
        return r

    def _get_end_frame_num(self):
        if self._end_frame_num is None:
            self._end_frame_num = self._ifvg.get_frame_count() - 10
        return self._end_frame_num

    def _setup_results_file(self):
        if self._get_results() is None:
            self._cdf.save_as_yml(self.__class__.RESULTS_TEMPLATE,
                                  self._results_data_dir_name,
                                  CalibrationDataFiler.FRAME_RATE_CALCULATION,
                                 )
        return self

    def _get_results(self):
        if self._results is None:
            self._results = self._cdf.load(self._results_data_dir_name,
                                           CalibrationDataFiler.FRAME_RATE_CALCULATION,
                                          )
        return self._results

    def _get_calculated_results(self):
        r = {}
        r[self.__class__.START_FRAME_NUM] = self._start_frame_num
        r[self.__class__.END_FRAME_NUM] = self._get_end_frame_num()
        r[self.__class__.NUM_FRAMES] = self._get_end_frame_num() - self._start_frame_num
        r[self.__class__.START_TIME_MS] = self._get_ms_from_hms(
            self._get_input_data(self.__class__.START, self.__class__.HOURS),
            self._get_input_data(self.__class__.START, self.__class__.MINUTES),
            self._get_input_data(self.__class__.START, self.__class__.SECONDS),
        )
        r[self.__class__.END_TIME_MS] = self._get_ms_from_hms(
            self._get_input_data(self.__class__.END, self.__class__.HOURS),
            self._get_input_data(self.__class__.END, self.__class__.MINUTES),
            self._get_input_data(self.__class__.END, self.__class__.SECONDS),
        )
        r[self.__class__.TIME_DIFF] = r[self.__class__.END_TIME_MS] - r[self.__class__.START_TIME_MS]
        r[self.__class__.FRAME_RATE] = 1000 * r[self.__class__.NUM_FRAMES] / r[self.__class__.TIME_DIFF]
        r[self.__class__.HEADER_FPS_CV2] = self._ifvg.get_frame_rate()
        r[self.__class__.VIDEO_ID] = self._ifvg.get_video_id()
        r[self.__class__.VIDEO_PATH] = str(self.__class__.CLOCK_VIDEO_PATH.resolve())


        results = self._get_results()
        results[self.__class__.CALCULATED_RESULTS] = r
        return results

    def _save_calculated_results(self):
        self._cdf.save_as_yml(self._get_calculated_results(),
                              self._results_data_dir_name,
                              CalibrationDataFiler.FRAME_RATE_CALCULATION,
                             )
        return self


    def _get_ms_from_hms(self, hours: int, minutes: int, seconds: float):
        return int(hours * 60 * 60 *1000 +\
                   minutes * 60 * 1000 +\
                   seconds * 1000)

    def _get_input_data(self, start_end, hms):
        return self._get_results()[self.__class__.INPUT_DATA][start_end][hms]

    def _show_ifvs(self):
        VerticalImageList(self._get_ifvs()).run()

    def run(self):
        self._setup_results_file()
        self._show_ifvs()
        self._save_calculated_results()
