import cv2
import PIL
import PIL.Image

class VideoHelper:

    def __init__(self, video_url):
        self.video_url = video_url
        self.cap = cv2.VideoCapture(video_url)

    def get_images_at_times_ms(self, times_ms):
        if not isinstance(times_ms, list):
            times_ms = [times_ms]
        return [self.get_image_at_msec(t) for t in times_ms]

    def get_image_at_msec(self, time_ms):
        self.cap.set(cv2.CAP_PROP_POS_MSEC, time_ms)
        success, array = self.cap.read()

        if not success:
            raise "Could not read frame ms = " + time_ms

        return PIL.Image.fromarray(array)
