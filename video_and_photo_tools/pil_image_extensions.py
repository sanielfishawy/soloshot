# pylint: disable=W0223, C0301
import PIL.Image

class ImageExtensions(PIL.Image.Image):

    def resize_with_width_preserve_aspect(self, width, resample=PIL.Image.ANTIALIAS, **kw):
        height = int(width / self.get_aspect())
        return self.resize((width, height), resample=resample, **kw)

    def resize_with_height_preserve_aspect(self, height, resample=PIL.Image.ANTIALIAS, **kw):
        width = int(height * self.get_aspect())
        return self.resize((width, height), resample=resample, **kw)

    def get_aspect(self):
        return self.width / self.height

PIL.Image.Image.resize_with_width_preserve_aspect = ImageExtensions.resize_with_width_preserve_aspect
PIL.Image.Image.resize_with_height_preserve_aspect = ImageExtensions.resize_with_height_preserve_aspect
PIL.Image.Image.get_aspect = ImageExtensions.get_aspect
