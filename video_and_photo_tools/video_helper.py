import sys
import os
from typing import List
from pathlib import Path
import cv2
import PIL
import PIL.Image

sys.path.insert(0, os.getcwd())
from video_and_photo_tools.image_from_video import ImageFromVideo

class VideoHelper:

    def __init__(self, video_url):
        self._video_url = Path(video_url)
        self._cap = cv2.VideoCapture(str(video_url.resolve()))
        self._frame_rate = None

    def get_image_from_video_at_frame_num(self, frame_num) -> ImageFromVideo:
        frame_num = self.bounded_frame_num(frame_num)
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        time_ms = self._cap.get(cv2.CAP_PROP_POS_MSEC)
        return ImageFromVideo(image=self._get_image_at_current_frame(),
                              time_ms=time_ms,
                              frame_num=frame_num,
                              video_url=self._video_url,
                             )

    def get_image_from_video_at_time_ms(self, time_ms):
        return self.get_image_from_video_at_frame_num(self.get_frame_num_for_time_ms(time_ms))

    def get_frame_num_for_time_ms(self, time_ms):
        self._cap.set(cv2.CAP_PROP_POS_MSEC, time_ms)
        return self._cap.get(cv2.CAP_PROP_POS_FRAMES)

    def get_time_ms_for_frame_num(self, frame_num):
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        return self._cap.get(cv2.CAP_PROP_POS_MSEC)

    def _get_image_at_current_frame(self):
        success, array = self._cap.read()
        if not success:
            raise "Could not read frame"
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
        return [self.get_image_from_video_at_frame_num(num) for num in frame_nums]

    # Fast because doing continuous reads
    def get_num_images_from_after_start_n(self, start_n, num):
        result = []
        start_n = self.bounded_frame_num(start_n)
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, start_n)
        time_ms = self._cap.get(cv2.CAP_PROP_POS_MSEC)
        time_per_frame = self.get_time_per_frame_ms()

        for idx in range(start_n, start_n + num):
            success, arr = self._cap.read()
            if not success:
                break

            ifv = ImageFromVideo(frame_num=idx,
                                 time_ms=time_ms,
                                 video_url=self._video_url,
                                 image=PIL.Image.fromarray(arr))

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
        return self.get_num_images_from_after_start_n(start, num)

    def get_images_around_time_ms(self, time_ms, before=10, after=10):
        return self.get_images_around_frame_number(self.get_frame_num_for_time_ms(time_ms),
                                                   before=before,
                                                   after=after)

    def get_frame_count(self):
        # Note that CAP_PROP_FRAME_COUNT is only an estimate so use the following method instead
        # Note CAP_PROP_POS_AVI_RATIO=1 positions 1 after the last frame. Therefore
        # no need to add 1 to get the zero based frame_count
        self._cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
        return self._cap.get(cv2.CAP_PROP_POS_FRAMES)

    def get_video_duration_ms(self):
        self._cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
        return self._cap.get(cv2.CAP_PROP_POS_MSEC)
