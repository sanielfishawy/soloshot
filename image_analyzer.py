import visual_angle_calculator as Vac
#       |------------x1----------0----------------------x2-|
#                     .          |                    .
#                      .         |                  .
#                       .        | d              .
#                        .       |              .
#                         .      |            .
#                          .     |          .
#                           .    |        .
#                            . a1|  a2  .
#                             .  |    .
#                              . |  .
#                               .|.
#                                c
#
#
# Moving from left to right gives postive subtended angles
# Moving from right to left gives negative subtended angles
# x from image generator may be positive (right of center screen) e.g. x2 or negative (left of center screen) e.g. x1
#
class ImageAnalyzer:

    def __init__(self, camera):
        self.camera = camera
        self.images = None

        self._image_width = self.camera.get_image_generator().get_image_width()
        self._fov_rad = self.camera.get_fov_rad()

    def set_images(self, images):
        self.images = images
        return self

    def get_subtended_angles_for_all_objects(self, timestamp1, timestamp2):
        objs_1 = self.images[timestamp1].keys()
        objs_2 = self.images[timestamp2].keys()
        objs = [obj for obj in objs_1 if obj in objs_2]

        r = {}
        for obj in objs:
            r[obj] = self._get_subtended_angle_with_obj_timestamps_rad(obj, timestamp1, timestamp2)

        return r

    def _get_x_with_object_and_timestamp(self, obj, timestamp):
        return self.images[timestamp][obj]

    def _get_subtended_angle_with_obj_timestamps_rad(self, obj, timestamp1, timestamp2):
        x_1 = self.images[timestamp1].get(obj, None)
        x_2 = self.images[timestamp2].get(obj, None)

        if x_1 is None or x_2 is None:
            return None
        else:
            return Vac.get_subtended_angle_with_x_rad(x_1, x_2, self._image_width, self._fov_rad)

    def _get_angle_relative_to_center_with_obj_timestamp_rad(self, obj, timestamp):
        x_pos = self.images[timestamp][obj]

        if x_pos is None:
            return None
        else:
            return Vac.get_angle_relative_to_center_with_x_rad(
                x_pos=x_pos,
                image_width=self._image_width,
                fov_rad=self._fov_rad,
            )

    def get_angles_relative_to_center_for_all_objects(self, timestamp):
        r = {}
        for obj in self.images[timestamp]:
            r[obj] = self._get_angle_relative_to_center_with_obj_timestamp_rad(obj, timestamp)
        return r
