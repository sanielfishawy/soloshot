# pylint: disable=C0413, W0212, C0301
import sys
import os
import unittest
from pathlib import Path

sys.path.insert(0, os.getcwd())
from geo_mapping.geo_mapper import GeoMapper, LatLongToPixelConverter, MapFitter
from legacy_data_pipeline.tag_gps_timebase_aligner import TagGpsTimebaseAligner
from tk_canvas_renderers.tk_geo_mapper import TkGeoMapper

class TestGeoMapper(unittest.TestCase):

    HEAD_PATH = Path('/Volumes/WD')
    TEST_SESSION_DIR_NAME = 'Aug_17_Palo_Alto_High_2nd_time_B80_ottofillmore'

    def setUp(self):
        self.tgta = TagGpsTimebaseAligner(self.__class__.TEST_SESSION_DIR_NAME)
        self.lat_long = self.tgta._get_first_lat_long()
        self.latitude_series = self.tgta.get_latitude_series()
        self.longitude_series = self.tgta.get_longitude_series()

    def test_map_fitter(self):
        map_fitter = MapFitter(self.latitude_series, self.longitude_series)
        map_fitter.get_map()

    def test_visualize_with_tk_geo_mapper(self):
        tk_geo_mapper = TkGeoMapper(self.latitude_series, self.longitude_series)
        tk_geo_mapper.run()

    def test_get_api_key(self):
        self.assertTrue(isinstance(GeoMapper()._get_google_maps_api_key(), str))

    def test_get_map(self):
        geo_mapper = GeoMapper(center_latitude=self.lat_long[0],
                               center_longitude=self.lat_long[1],
                              )
        geo_mapper.get_map()

    def test_get_map_with_markers(self):
        geo_mapper = GeoMapper(center_latitude=self.lat_long[0],
                               center_longitude=self.lat_long[1],
                               add_markers=True,
                              )
        geo_mapper.get_map()

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
