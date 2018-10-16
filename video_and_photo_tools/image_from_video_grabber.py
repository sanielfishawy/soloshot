import sys
import os
from typing import List
from pathlib import Path
import cv2
import PIL
import PIL.Image

sys.path.insert(0, os.getcwd())
from video_and_photo_tools.image_from_video import ImageFromVideo # pylint: disable=C0413
from video_and_photo_tools.image_cache import ImageCache # pylint: disable=C0413
import video_and_photo_tools.pil_image_extensions # pylint: disable=C0413, W0611

class ImageFromVideoGrabber:

    IMAGE_MODE_L = 'L'
    IMAGE_MODE_RGB = 'RGB'
    IMAGE_FORMAT_JPG = 'jpg'
    IMAGE_FORMAT_PNG = 'png'
    IMAGE_FORMAT_PPM = 'ppm'
    IMAGE_FORMAT_BMP = 'bmp'

    def __init__(self,
                 video_url,
                 image_mode='L',
                 image_width=640,
                 image_format='jpg',
                 use_cache=True,
                 cache_dir_path=None):

        self._video_url = Path(video_url)
        self._image_mode = image_mode
        self._image_width = image_width
        self._image_format = image_format

        self._cap = cv2.VideoCapture(str(video_url.resolve()))
        self._frame_rate = None
        self._use_cache = use_cache
        self._cache_dir_path = cache_dir_path
        self._image_cache = ImageCache(cache_dir_path=cache_dir_path)
        self._frame_count = None
        self.get_frame_count()

    def get_video_id(self):
        return self._video_url.name + '-' + str(os.path.getsize(self._video_url))

    def get_image_at_frame_num(self, frame_num) -> ImageFromVideo:
        i_f_v = self.get_image_from_cache_at_frame_num(frame_num)
        if i_f_v is None:
            return self.get_image_from_video_at_frame_num(frame_num)

        return i_f_v

    # Used for multi image grabs
    def get_image_from_cache_at_frame_num(self, frame_num, time_ms=None) -> ImageFromVideo:
        if not self._use_cache:
            return None

        frame_num = self.bounded_frame_num(frame_num)
        image = self._image_cache.fetch(self.get_video_id(),
                                        self._image_width,
                                        self._image_mode,
                                        frame_num,
                                        self._image_format)

        if image is None:
            return None

        from_cache = True
        if time_ms is None:
            time_ms = self.get_time_ms_for_frame_num(frame_num)

        return self._get_image_from_video_object(image,
                                                 time_ms,
                                                 frame_num,
                                                 from_cache,
                                                )

    # Not used for multi image grabs.
    def get_image_from_video_at_frame_num(self, frame_num) -> ImageFromVideo:
        frame_num = self.bounded_frame_num(frame_num)
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        time_ms = self._cap.get(cv2.CAP_PROP_POS_MSEC)

        image = self._get_image_at_current_frame()
        image = self._adust_image_width_mode(image)

        self._store_in_cache(image, frame_num)

        from_cache = False
        return self._get_image_from_video_object(image, time_ms, frame_num, from_cache)

    def _adust_image_width_mode(self, image):
        image = image.convert(self._image_mode)
        return image.resize_with_width_preserve_aspect(self._image_width)

    def _store_in_cache(self, image, frame_num):
        if self._use_cache:
            self._image_cache.store(self.get_video_id(),
                                    image,
                                    frame_num,
                                    self._image_format)

    def _get_image_from_video_object(self, image, time_ms, frame_num, from_cache):
        return ImageFromVideo(image=image,
                              time_ms=int(time_ms),
                              frame_num=frame_num,
                              video_url=self._video_url,
                              video_id=self.get_video_id(),
                              from_cache=from_cache,
                             )

    # Not used for multi image grabs.
    def get_image_from_video_at_time_ms(self, time_ms):
        return self.get_image_at_frame_num(self.get_frame_num_for_time_ms(time_ms))

    def get_frame_num_for_time_ms(self, time_ms):
        self._cap.set(cv2.CAP_PROP_POS_MSEC, time_ms)
        return self._cap.get(cv2.CAP_PROP_POS_FRAMES)

    def get_time_ms_for_frame_num(self, frame_num):
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        return self._cap.get(cv2.CAP_PROP_POS_MSEC)

    def _get_image_at_current_frame(self):
        success, array = self._cap.read()
        assert success, 'Could not read frame'
        return PIL.Image.fromarray(array)

    def bounded_frame_num(self, frame_num):
        frame_num = int(frame_num)
        if frame_num < 0:
            return 0

        if frame_num >= self.get_frame_count():
            return int(self.get_frame_count() - 1)

        return frame_num

    # Slow because doing random access reads
    def get_images_from_video_at_times_ms(self, times_ms: list) -> List[ImageFromVideo]:
        return [self.get_image_from_video_at_time_ms(t) for t in times_ms]

    # Slow because doing random access reads
    def get_images_from_video_at_frame_nums(self, frame_nums: list) -> List[ImageFromVideo]:
        return [self.get_image_at_frame_num(num) for num in frame_nums]

    # Usef for multi image grabs
    # Fast because doing continuous reads
    def get_num_images_from_video_after_start_n(self, start_n, num):
        result = []
        start_n = self.bounded_frame_num(start_n)

        self._cap.set(cv2.CAP_PROP_POS_FRAMES, start_n)
        time_ms = self._cap.get(cv2.CAP_PROP_POS_MSEC)
        time_per_frame = self.get_time_per_frame_ms()
        got_from_cache = False

        for frame_num in range(start_n, start_n + num):

            ifv = self.get_image_from_cache_at_frame_num(frame_num, time_ms=time_ms)

            if ifv is not None:
                got_from_cache = True

            else:
                # If we got from the cache previously then read position has not been advancing
                # so do it manually
                if got_from_cache:
                    self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                got_from_cache = False

                success, arr = self._cap.read()
                if not success:
                    break

                image = PIL.Image.fromarray(arr)
                image = self._adust_image_width_mode(image)
                self._store_in_cache(image, frame_num)
                from_cache = False
                ifv = self._get_image_from_video_object(image,
                                                        time_ms,
                                                        frame_num,
                                                        from_cache,
                                                       )


            result.append(ifv)
            time_ms += time_per_frame

        return result

    def get_frame_rate(self):
        if self._frame_rate is None:
            self._frame_rate = self._cap.get(cv2.CAP_PROP_FPS)
        return self._frame_rate

    def get_time_per_frame_ms(self):
        return 1000 / self.get_frame_rate()

    def get_images_around_frame_number(self, frame_num, before=10, after=10):
        start = self.bounded_frame_num(frame_num - before)
        end = self.bounded_frame_num(frame_num + after)
        num = end - start
        return self.get_num_images_from_video_after_start_n(start, num)

    def get_images_around_time_ms(self, time_ms, before=10, after=10):
        return self.get_images_around_frame_number(self.get_frame_num_for_time_ms(time_ms),
                                                   before=before,
                                                   after=after)

    def get_frame_count(self):
        # Note that CAP_PROP_FRAME_COUNT is only an estimate so use the following method instead
        # Note CAP_PROP_POS_AVI_RATIO=1 positions 1 after the last frame. Therefore
        # no need to add 1 to get the zero based frame_count
        if self._frame_count is None:
            self._cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
            self._frame_count = self._cap.get(cv2.CAP_PROP_POS_FRAMES)
        return self._frame_count

    def get_video_duration_ms(self):
        self._cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
        return self._cap.get(cv2.CAP_PROP_POS_MSEC)
