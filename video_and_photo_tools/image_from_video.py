from typing import Dict
from pathlib import Path
import PIL.Image

class ImageFromVideo:

    # Keys
    FRAME_NUM = 'frame_num'
    TIME_MS = 'time_ms'
    VIDEO_URL = 'video_url'
    VIDEO_ID = 'video_id'

    def __init__(self,
                 image: PIL.Image.Image,
                 frame_num=None,
                 time_ms=None,
                 video_url=None,
                 video_id=None,
                 from_cache=False):

        self._image = image
        self._frame_num = frame_num
        self._time_ms = time_ms
        self._video_path = Path(video_url)
        self._video_id = video_id
        self._from_cache = from_cache

    def set_image(self, image: PIL.Image.Image):
        self._image = image
        return self

    def set_frame_num(self, frame_num):
        self._frame_num = frame_num
        return self

    def set_time_ms(self, time_ms):
        self._time_ms = time_ms
        return self

    def set_video_path(self, video_path):
        self._video_path = Path(video_path)
        return self

    def set_video_id(self, video_id):
        self._video_id = video_id
        return self

    def set_from_cache(self, from_cache):
        self._from_cache = from_cache
        return self

    def get_image(self) -> PIL.Image:
        return self._image

    def get_frame_num(self):
        return self._frame_num

    def get_formatted_frame_num(self):
        return '{:,}'.format(self.get_frame_num())

    def get_time_ms(self):
        return self._time_ms

    def get_formatted_time_ms(self):
        return '{:,}'.format(self.get_time_ms())

    def get_video_path(self) -> Path:
        return self._video_path

    def get_video_id(self) -> str:
        return self._video_id

    def get_from_cache(self) -> bool:
        return self._from_cache

    def get_as_dict(self) -> Dict:
        return {
            self.__class__.FRAME_NUM: self.get_frame_num(),
            self.__class__.TIME_MS: self.get_time_ms(),
            self.__class__.VIDEO_URL: str(self.get_video_path().resolve()),
            self.__class__.VIDEO_ID: self.get_video_id(),
        }
