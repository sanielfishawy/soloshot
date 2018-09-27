from pathlib import Path
import PIL.Image

class ImageFromVideo:

    def __init__(self, image: PIL.Image.Image, frame_num=None, time_ms=None, video_url=None):
        self._image = image
        self._frame_num = frame_num
        self._time_ms = time_ms
        self._video_url = Path(video_url)

    def set_image(self, image: PIL.Image.Image):
        self._image = image
        return self

    def set_frame_num(self, frame_num):
        self._frame_num = frame_num
        return self

    def set_time_ms(self, time_ms):
        self._time_ms = time_ms
        return self

    def set_video_url(self, video_url):
        self._video_url = Path(video_url)
        return self

    def get_image(self) -> PIL.Image:
        return self._image

    def get_frame_num(self):
        return self._frame_num

    def get_time_ms(self):
        return self._time_ms

    def get_video_url(self) -> Path:
        return self._video_url
