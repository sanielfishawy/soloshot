import os
from pathlib import Path
import PIL.Image

class ImageCache:

    DEFAULT_IMAGE_CACHE_DIR_PATH = Path('.') / 'data/image_cache'

    VALID_SUFFIXES = [
        'jpg',
        'png',
        'ppm',
        'bmp'
    ]
    def __init__(self, cache_dir_path=None):
        self.cache_dir_path = cache_dir_path
        if self.cache_dir_path is None:
            self.cache_dir_path = ImageCache.DEFAULT_IMAGE_CACHE_DIR_PATH

        self._ensure_cache_dir()

    def store(self, video_id, image: PIL.Image, frame_num, image_format):
        image.save(self._get_filepath(video_id, image.width, image.mode, frame_num, image_format))

    def fetch(self, video_id, width, mode, frame_num, image_format):
        filepath = self._get_filepath(video_id, width, mode, frame_num, image_format)

        assert self._is_exist_cache_dir(), 'Image Cache Directory not found'

        if not self._is_exist_file(filepath):
            return None

        return PIL.Image.open(filepath)

    def _is_exist_file(self, filepath):
        return os.path.isfile(filepath)

    def _is_exist_cache_dir(self):
        return os.path.isdir(self.cache_dir_path)

    def _ensure_cache_dir(self):
        relative_to_py_root = self.cache_dir_path.relative_to(Path('.'))
        path = Path('.')
        for part in relative_to_py_root.parts:
            path = path / part
            if not os.path.isdir(path):
                os.mkdir(path)
        return self

    def _get_filename(self, video_id, width, mode, frame_num, image_format):
        return f'{video_id}-width={width}-mode={mode}-frame_num={frame_num}.{image_format.lower()}'

    def _get_filepath(self, video_id, width, mode, frame_num, image_format):
        return self.cache_dir_path / self._get_filename(video_id,
                                                        width,
                                                        mode,
                                                        frame_num,
                                                        image_format)

    def clear_cache(self):
        self._ensure_cache_dir()
        for suffix in ImageCache.VALID_SUFFIXES:
            for image_file in list(self.cache_dir_path.glob('*.' + suffix)):
                os.remove(image_file)
        return self

    def destroy_cache_dir(self):
        self.clear_cache()
        os.rmdir(self.cache_dir_path)
