# pylint: disable=protected-access
import os
import yaml
from pathlib import Path
import timeit
import tkinter
import cv2
import PIL.Image
import PIL.ImageTk

class _VideoImageBenchmarks:

    VIDEO_PATH = Path('.') / 'data/test_data/test_videos/video.mp4'
    VIDEO_PATH_STR = str(VIDEO_PATH.resolve())
    IMAGE_DIR_PATH = Path('.') / 'data/test_data/test_images'
    FORMAT_JPG = 'jpeg'
    FORMAT_PPM = 'ppm'
    FORMAT_PNG = 'png'
    FORMAT_BMP = 'bmp'
    FORMATS = [
        FORMAT_BMP,
        FORMAT_JPG,
        FORMAT_PNG,
        FORMAT_PPM
    ]

    def __init__(self):
        self._cap = cv2.VideoCapture(_VideoImageBenchmarks.VIDEO_PATH_STR)
        self.tk = tkinter.Tk()
        self._cap_arr = None
        self._rgb_image_large = None
        self._l_image_large = None
        self._rgb_image_640 = None
        self._l_image_640 = None

    def setup(self):
        # Make sure they are in memory
        self._get_cap_array()
        self._get_rgb_image_large()
        self._get_l_image_large()
        self._get_rgb_image_640()
        self._get_l_image_640()
        self.save_bmp_benchmark()
        self.save_jpg_benchmark()
        self.save_png_benchmark()
        self.save_ppm_benchmark()

    def cv2_read_benchmark_setup(self):
        self._cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 0)

    def cv2_read_benchmark(self):
        success, _ = self._cap.read()
        if not success:
            raise Exception("Failed VideoCapture.read()")

    def convert_array_to_image_benchmark(self):
        image = PIL.Image.fromarray(self._get_cap_array())
        assert image.width > 0, "Problem loading image from array"

    def convert_rgb_to_l_benchmark(self):
        l_image = self._get_rgb_image_large().convert('L')
        assert l_image.mode is 'L', 'Problem converting RGB to L'

    def resize_rgb_image_benchmark(self):
        self._resize_image(self._get_rgb_image_large())

    def resize_l_image_benchmark(self):
        self._resize_image(self._get_l_image_large())

    def convert_640_rgb_to_tk_image_benchmark(self):
        tk_640_rgb = PIL.ImageTk.PhotoImage(image=self._get_rgb_image_640())
        assert tk_640_rgb._PhotoImage__size == (640, 360)
        assert tk_640_rgb._PhotoImage__mode == 'RGB'

    def convert_640_l_to_tk_image_benchmark(self):
        tk_640_l = PIL.ImageTk.PhotoImage(image=self._get_l_image_640())
        assert tk_640_l._PhotoImage__size == (640, 360)
        assert tk_640_l._PhotoImage__mode == 'L'

    def save_jpg_benchmark(self):
        self._save_image(self._get_l_image_640(), _VideoImageBenchmarks.FORMAT_JPG)

    def save_ppm_benchmark(self):
        self._save_image(self._get_l_image_640(), _VideoImageBenchmarks.FORMAT_PPM)

    def save_png_benchmark(self):
        self._save_image(self._get_l_image_640(), _VideoImageBenchmarks.FORMAT_PNG)

    def save_bmp_benchmark(self):
        self._save_image(self._get_l_image_640(), _VideoImageBenchmarks.FORMAT_BMP)

    def open_jpg_benchmark(self):
        self._open_image('L', '640', _VideoImageBenchmarks.FORMAT_JPG)

    def open_png_benchmark(self):
        self._open_image('L', '640', _VideoImageBenchmarks.FORMAT_PNG)

    def open_bmp_benchmark(self):
        self._open_image('L', '640', _VideoImageBenchmarks.FORMAT_BMP)

    def open_ppm_benchmark(self):
        self._open_image('L', '640', _VideoImageBenchmarks.FORMAT_PPM)

    def _open_image(self, mode, width, image_format):
        PIL.Image.open(self._get_image_path(mode, width, image_format))

    def _save_image(self, image, image_format):
        image.save(self._get_image_path_with_image(image, image_format), image_format)

    def _get_image_path(self, mode, width, image_format):
        return self._get_image_path_with_filename(self._get_image_filename(mode,
                                                                           width,
                                                                           image_format))

    def _get_image_path_with_filename(self, image_filename):
        return str((_VideoImageBenchmarks.IMAGE_DIR_PATH / image_filename).resolve())

    def _get_image_filename(self, mode, width, image_format):
        return 'image-' + mode + '-' + str(width) + '.' + image_format.lower()

    def _get_image_path_with_image(self, image, image_format):
        return self._get_image_path(image.mode, image.width, image_format)


    def _resize_image(self, image: PIL.Image.Image):
        aspect = image.width / image.height
        height = int(640 / aspect)
        image_640_l = image.resize((640, height), resample=PIL.Image.ANTIALIAS)
        assert image_640_l.width == 640, 'Problem resizing to 640'

    def _get_cap_array(self):
        if self._cap_arr is None:
            self._cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 0)
            success, self._cap_arr = self._cap.read()
            if not success:
                raise Exception("Failed VideoCapture.read()")

        return self._cap_arr

    def _get_rgb_image_large(self) -> PIL.Image.Image:
        if self._rgb_image_large is None:
            self._rgb_image_large = PIL.Image.fromarray(self._get_cap_array())
        return self._rgb_image_large

    def _get_l_image_large(self) -> PIL.Image.Image:
        if self._l_image_large is None:
            self._l_image_large = self._get_rgb_image_large().convert('L')
            assert self._l_image_large.mode is 'L', 'Problem converting RGB -> L'
            assert self._l_image_large.width > 640
        return self._l_image_large

    def _get_rgb_image_640(self) -> PIL.Image.Image:
        if self._rgb_image_640 is None:
            width = self._get_rgb_image_large().width
            aspect = width / self._get_rgb_image_large().height
            height = int(640 / aspect)
            self._rgb_image_640 = self._get_rgb_image_large().resize((640, height), resample=PIL.Image.ANTIALIAS)
            assert self._rgb_image_640.mode == 'RGB', 'Problem getting RGB 640'
            assert self._rgb_image_640.width == 640, 'Problem getting RGB 640'
        return self._rgb_image_640

    def _get_l_image_640(self) -> PIL.Image.Image:
        if self._l_image_640 is None:
            self._l_image_640 = self._get_rgb_image_640().convert('L')
            assert self._l_image_640.mode == 'L', 'Problem getting L 640'
            assert self._l_image_640.width == 640, 'Problem getting L 640'
        return self._l_image_640

class _VideoImageBenchmarkRunner:

    TOTAL_TIME = 'total_time'
    NUM_RUNS = 'num_runs'
    TIME_PER = 'time_per'
    RESULTS_FILE_PATH = Path('.') / 'video_and_photo_tools/video_image_benchmark_results.yml'

    def __init__(self):
        VideoImageBenchmarks() #init
        self._num_runs = 10
        self._results = {}

    def run_benchmarks(self, benchmarks):
        for b_m in benchmarks:
            if not isinstance(b_m, str):
                b_m = b_m.__name__
            self._run_benchmark(b_m)

    def _run_benchmark(self, benchmark_name: str):
        VideoImageBenchmarks().setup()

        b_setup_name = benchmark_name + '_setup'
        if b_setup_name in dir(VideoImageBenchmarks()):
            getattr(VideoImageBenchmarks(), b_setup_name)()

        total_time = self._time_benchmark(benchmark_name)
        self._results[benchmark_name] = self._get_result(total_time, self._num_runs)

    def _time_benchmark(self, benchmark_name: str):
        return timeit.timeit('VideoImageBenchmarks().' + benchmark_name + '()',
                             setup='from __main__ import VideoImageBenchmarks',
                             number=self._num_runs,
                            )

    def _get_result(self, total_time, num_runs):
        return {
            _VideoImageBenchmarkRunner.TOTAL_TIME: round(total_time, 4),
            _VideoImageBenchmarkRunner.NUM_RUNS: round(num_runs, 4),
            _VideoImageBenchmarkRunner.TIME_PER: round(total_time / num_runs, 4),
        }

    def log_image_sizes(self):
        VideoImageBenchmarks().setup()
        r = {}
        for iformat in _VideoImageBenchmarks.FORMATS:
            filename = 'image-L-640.' + iformat
            path = str((_VideoImageBenchmarks.IMAGE_DIR_PATH / filename).resolve())
            r[filename] = os.path.getsize(path)
        self._results['Image File Sizes'] = r

    def get_results(self):
        return self._results

    def dump_results(self):
        with open(_VideoImageBenchmarkRunner.RESULTS_FILE_PATH, 'w') as yaml_file:
            yaml.dump(self._results, yaml_file, default_flow_style=False)

_video_image_benchmark_runner = None

def VideoImageBenchmarkRunner():
    global _video_image_benchmark_runner
    if _video_image_benchmark_runner is None:
        _video_image_benchmark_runner = _VideoImageBenchmarkRunner()
    return _video_image_benchmark_runner

_video_image_benchmarks = None

def VideoImageBenchmarks():
    global _video_image_benchmarks
    if _video_image_benchmarks is None:
        _video_image_benchmarks = _VideoImageBenchmarks()
    return _video_image_benchmarks


if __name__ == '__main__':
    b_marks = [
        VideoImageBenchmarks().cv2_read_benchmark,
        VideoImageBenchmarks().convert_array_to_image_benchmark,
        VideoImageBenchmarks().convert_rgb_to_l_benchmark,
        VideoImageBenchmarks().resize_l_image_benchmark,
        VideoImageBenchmarks().resize_rgb_image_benchmark,
        VideoImageBenchmarks().convert_640_rgb_to_tk_image_benchmark,
        VideoImageBenchmarks().convert_640_l_to_tk_image_benchmark,
        VideoImageBenchmarks().save_jpg_benchmark,
        VideoImageBenchmarks().save_bmp_benchmark,
        VideoImageBenchmarks().save_png_benchmark,
        VideoImageBenchmarks().save_ppm_benchmark,
        VideoImageBenchmarks().open_jpg_benchmark,
        VideoImageBenchmarks().open_bmp_benchmark,
        VideoImageBenchmarks().open_png_benchmark,
        VideoImageBenchmarks().open_ppm_benchmark,
    ]
    VideoImageBenchmarkRunner().run_benchmarks(b_marks)
    VideoImageBenchmarkRunner().log_image_sizes()
    VideoImageBenchmarkRunner().dump_results()
