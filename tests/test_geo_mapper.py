# pylint: disable=C0413, W0212, C0301
import sys
import os
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0, os.getcwd())
from geo_mapping.geo_mapper import GeoMapper, LatLongToPixelConverter, MapFitter, MapCoordinateTransformer
from tk_canvas_renderers.tk_geo_mapper import TkGeoMapper
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper

class TestGeoMapper(unittest.TestCase):

    HEAD_PATH = Path('/Volumes/WD')
    SESSION_DIR = 'Aug_17_Palo_Alto_High_2nd_time_B80_ottofillmore'

    def setUp(self):
        ldfh = LegacyDataFileSystemHelper(
            head_path=self.__class__.HEAD_PATH,
        )
        self.latitude_series = ldfh.get_field_from_npz_file(
            session_dir_name=self.__class__.SESSION_DIR,
            filename=LegacyDataFileSystemHelper.TAG_NPZ_FILE,
            fieldname=LegacyDataFileSystemHelper.TAG_LATITUDE_FIELD,
        )
        self.longitude_series = ldfh.get_field_from_npz_file(
            session_dir_name=self.__class__.SESSION_DIR,
            filename=LegacyDataFileSystemHelper.TAG_NPZ_FILE,
            fieldname=LegacyDataFileSystemHelper.TAG_LONGITUDE_FIELD,
        )
        self.time_series = ldfh.get_field_from_npz_file(
            session_dir_name=self.__class__.SESSION_DIR,
            filename=LegacyDataFileSystemHelper.TAG_NPZ_FILE,
            fieldname=LegacyDataFileSystemHelper.TAG_TIME_FIELD,
        )
        self.lat_long = self.latitude_series[0], self.longitude_series[0]

    def test_longitude_deg_per_pixel(self):
        max_latitude = np.max(self.latitude_series)
        min_latitude = np.min(self.latitude_series)
        long_scale_factor_max_latitude = LatLongToPixelConverter()._long_vs_lat_scale_factor(max_latitude)
        long_scale_factor_min_latitude = LatLongToPixelConverter()._long_vs_lat_scale_factor(min_latitude)
        scale_factor_ratio = long_scale_factor_max_latitude / long_scale_factor_min_latitude
        self.assertNotEqual(scale_factor_ratio, 1)
        self.assertAlmostEqual(scale_factor_ratio, 1, places=4)

    def dont_test_map_fitter(self):
        map_fitter = MapFitter(self.latitude_series, self.longitude_series)
        map_fitter.get_map()

    def dont_test_visualize_with_tk_geo_mapper(self):
        marker_positions = [
            [37.3865785, -122.11006499999999],
            [37.38673475, -122.10986187499999],
            [37.38673475, -122.11026812499999],
            [37.386422249999995, -122.10986187499999],
            [37.386422249999995, -122.11026812499999],
        ]
        tk_geo_mapper = TkGeoMapper(self.latitude_series,
                                    self.longitude_series,
                                   )
        tk_geo_mapper.run()


    def test_map_coordinate_transformer_places_center_lat_long_in_center_of_map(self):
        for width in [200, 300, 640]:
            for height in [200, 300, 640]:
                for zoom in [18, 19, 20, 21]:
                    for scale in [1, 2]:
                        center_latitude = 37.3865785
                        center_longitude = -122.11006499999999

                        GeoMapper(center_latitude=center_latitude,
                                  center_longitude=center_longitude,
                                  size=f'{width}x{height}',
                                  zoom=zoom,
                                  scale=scale,
                                  add_markers=True,
                                 ).get_map()

                        map_coordinate_transformer = MapCoordinateTransformer(center_latitude,
                                                                              center_longitude,
                                                                              width,
                                                                              height,
                                                                              zoom,
                                                                              scale,
                                                                             )

                        center_x = map_coordinate_transformer.get_x_for_longitude(center_longitude)
                        center_y = map_coordinate_transformer.get_y_for_latitude(center_latitude)
                        print('width', width, 'height', height, 'zoom', zoom, 'scale', scale, 'center_x', center_x, 'center_y', center_y)

                        self.assertEqual(int(width/2), center_x)
                        self.assertEqual(int(height/2), center_y)

    def test_get_api_key(self):
        self.assertTrue(isinstance(GeoMapper()._get_google_maps_api_key(), str))

    def dont_test_get_map(self):
        geo_mapper = GeoMapper(center_latitude=self.lat_long[0],
                               center_longitude=self.lat_long[1],
                              )
        geo_mapper.get_map()

    def dont_test_get_map_with_markers(self):
        for zoom in [17, 18, 19, 20, 21]:
            GeoMapper(center_latitude=self.lat_long[0],
                      center_longitude=self.lat_long[1],
                      add_markers=True,
                      zoom=zoom,
                     ).get_map()

    def dont_test_get_lat_long_pixel_converter_info(self):
        info = LatLongToPixelConverter().get_info()
        print(info)
        for zoom in info:
            print('zoom=', zoom, 'multiple=', info[zoom]/info[21])

    def test_lat_long_to_pixel_converter(self):
        lat_long_to_pixel_converter = LatLongToPixelConverter()

        latitude_deg = LatLongToPixelConverter.LATITUDE

        measured_lat_height_pixels = lat_long_to_pixel_converter.LATITUDE_HEIGHT_PIXELS
        lat_height_deg = lat_long_to_pixel_converter.LATITUDE_HEIGHT_DEG
        measured_lat_deg_per_pix = lat_height_deg / measured_lat_height_pixels

        measured_long_width_pixels = lat_long_to_pixel_converter.LONGITUDE_WIDTH_PIXELS
        long_width_deg = lat_long_to_pixel_converter.LONGITUDE_WIDTH_DEG
        measured_long_deg_per_pix = long_width_deg / measured_long_width_pixels

        for scale in [1, 2]:
            for zoom in [20, 21]:
                m_lat_d_p_p = (22 - zoom) * (measured_lat_deg_per_pix / scale)
                calculated_lat_deg_per_pix = lat_long_to_pixel_converter.get_latitude_deg_per_pixel(zoom, scale)
                self.assertAlmostEqual(m_lat_d_p_p, calculated_lat_deg_per_pix)

                m_long_d_p_p = (22 - zoom) * (measured_long_deg_per_pix / scale)
                calculated_long_deg_per_pix = lat_long_to_pixel_converter.get_longitude_deg_per_pixel(latitude_deg, zoom, scale)
                self.assertAlmostEqual(m_long_d_p_p, calculated_long_deg_per_pix)


if __name__ == '__main__':
    unittest.main()
