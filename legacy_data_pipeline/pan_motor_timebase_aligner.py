# pylint: disable=C0413
import sys
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import numpy_extensions.numpy_ndarray_extensions # pylint: disable=W0611

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper as LDFH
from video_and_photo_tools.image_from_video_grabber import ImageFromVideoGrabber
from tk_canvas_renderers.scrub_picker import ScrubPicker

class PanMotorTimeBaseAligner:
    '''Determines with user assistance via scrubber picker statistics for offset in
       time between pan_motor_read timebase and video time'''

    TOP_LEVEL_HEAD_PATH = Path('/Volumes/WD')
    CACHE_DIR_PATH = Path('/Volumes/WD/image_cache')

    def __init__(self, session_dir: Path):
        self.session_dir = session_dir

        self.ldfh = LDFH(self.__class__.TOP_LEVEL_HEAD_PATH)

        self.maxima_text_color = 'red'
        self.minima_text_color = 'green'
        self.fontsize = 8

        # Lazy initializers
        self.pan_motor_read_data = None
        self.base_time = None
        self.motor_local_maxima = None
        self.motor_local_minima = None

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
        return self.motor_local_maxima

    def get_motor_values_at_maxima(self):
        return np.array([self.get_motor_data()[idx] for idx in self.get_motor_maxima()])

    def get_time_at_maxima(self):
        return np.array([self.get_normalized_base_time()[maximum]
                         for maximum in self.get_motor_maxima()])

    def get_motor_minima(self):
        if self.motor_local_minima is None:
            self.motor_local_minima = self.get_motor_data().\
                                           local_minima_sorted_by_peakyness_and_monotonic_with_steep_shoulders(8, 4, 2) # pylint: disable=C0301
        return self.motor_local_minima

    def get_motor_values_at_minima(self):
        return np.array([self.get_motor_data()[idx] for idx in self.get_motor_minima()])

    def get_time_at_minima(self):
        return np.array([self.get_normalized_base_time()[minimum]
                         for minimum in self.get_motor_minima()])

    def show_scrub_picker_for_maxima(self):
        for time in self.get_time_at_maxima():
            print(time)
            self.show_scrub_picker_for_time(time)

    def show_scrub_picker_for_minima(self):
        for time in self.get_time_at_minima():
            print(time)
            self.show_scrub_picker_for_time(time)

    def show_scrub_picker_for_time(self, time):
        ScrubPicker(images_from_video=self.get_images_around_time(time),
                    selector_type=ScrubPicker.SELECT_SINGLE_IMAGE).run()


    def get_images_around_time(self, time):
        return self.get_ifv_grabber().get_images_around_time_ms(time, before=40, after=40)

    def get_motor_data(self) -> np.ndarray:
        if self.pan_motor_read_data is None:
            self.pan_motor_read_data = self.ldfh.get_field_from_npz_file(self.session_dir,
                                                                         LDFH.BASE_NPZ_FILE,
                                                                         LDFH.PAN_MOTOR_READ_FIELD,
                                                                         )
        return self.pan_motor_read_data

    def get_base_time(self):
        if self.base_time is None:
            self.base_time = self.ldfh.get_field_from_npz_file(self.session_dir,
                                                               LDFH.BASE_NPZ_FILE,
                                                               LDFH.BASE_TIME_FIELD,
                                                              )
        return self.base_time

    def get_normalized_base_time(self):
        return self.get_base_time() - self.get_base_time()[0]

    def get_motor_data_time_tuples(self):
        return np.dstack((self.get_normalized_base_time(), self.get_motor_data()))[0]

    def get_video_path(self):
        return self.ldfh.get_video_path(self.session_dir)

    def get_ifv_grabber(self) -> ImageFromVideoGrabber:
        return ImageFromVideoGrabber(self.get_video_path(),
                                     cache_dir_path=self.__class__.CACHE_DIR_PATH)



