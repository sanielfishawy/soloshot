from pathlib import Path
import shutil
import urllib
import math
import requests
import yaml
import numpy as np

class GeoMapper:
    '''Interface to google static maps api. Downloads, caches and returns maps.'''

    API_KEY_PATH = Path('./credentials/google_api_keys.yml')
    API_KEY_NAME = 'google_maps_api_key'
    MAPS_URL = 'https://maps.googleapis.com/maps/api/staticmap'

    MAP_CACHE_DIR_PATH = Path('./data/maps')

    def __init__(self,
                 center_latitude=None,
                 center_longitude=None,
                 center='Brooklyn+Bridge,New+York,NY',
                 image_format='png',
                 zoom=20,
                 size='640x640',
                 maptype='satellite',
                 scale=1,
                 add_markers=False
                ):

        self._add_markers = add_markers
        self._center = center
        self._center_latitude = center_latitude
        self._center_longitude = center_longitude
        self._image_format = image_format
        self._zoom = zoom
        self._size = size
        self._maptype = maptype
        self._scale = scale

        # lazy inits
        self._api_key = None

    def get_map(self):
        if self._map_is_in_cache():
            print('Getting map from cache')
            return self._get_map_image_path()
        else:
            print('Getting map from google')
            return self._get_map_from_google()

    def _get_map_from_google(self):
        r = requests.get(self.__class__.MAPS_URL,
                         params=self._get_params(),
                         stream=True,
                        )

        assert r.status_code == 200,\
               f'Got a non 200 status ({r.status_code}) from http request for google maps.'

        with open(self._get_map_image_path(), 'wb') as image_file:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, image_file)

        return self._get_map_image_path()

    def _map_is_in_cache(self) -> bool:
        return self._get_map_image_path().is_file()

    def _get_params(self):
        r = {
            'format': self._image_format,
            'center': self._get_center(),
            'zoom': self._zoom,
            'size': self._size,
            'maptype': self._maptype,
            'scale': self._scale,
            'key': self._get_google_maps_api_key(),
        }

        if self._add_markers:
            r['markers'] = f'size:tiny|{self._get_marker_locations()}'

        return r

    def _get_center(self):
        if self._center_latitude is not None and self._center_latitude is not None:
            return f'{self._center_latitude},{self._center_longitude}'

        return self._center

    def _get_map_image_path(self):
        return self.__class__.MAP_CACHE_DIR_PATH / self._get_map_image_filename()

    def _get_map_image_filename(self):
        return urllib.parse.urlencode(self._get_params_sans_api_key()) + f'.{self._image_format}'

    def _get_params_sans_api_key(self):
        return {key: value
                for key, value in self._get_params().items()
                if key != 'key' and key != 'markers'
               }

    def _get_google_maps_api_key(self):
        if self._api_key is None:
            assert self.__class__.API_KEY_PATH.is_file(), \
                f'No api key yml file found at: {self.__class__.API_KEY_PATH.resolve()}'

            with open(self.__class__.API_KEY_PATH, 'r') as stream:
                api_keys = yaml.load(stream)

            self._api_key = api_keys[self.__class__.API_KEY_NAME]

        return self._api_key


    def _get_marker_locations(self):
        assert self._center_latitude is not None and self._center_longitude is not None,\
               '_get_marker_locations needs center lat and long'

        long_scale = 1.3
        offset = 110 * self.deg_lat_per_foot()
        # offset = (22 - self._zoom) * offset
        # if self._zoom == 17:
        #     offset = 2.5 * offset

        # print(f'Center latitude = {self._center_latitude}')
        # print(f'Center longitude = {self._center_longitude}')
        print('zoom=', self._zoom, 'scale=', self._scale)
        print(f'Latitude height = {2 * offset}')
        print(f'Longitude width = {2 * (long_scale * offset)}')

        r = (
            f'{self._center_latitude},{self._center_longitude}|'
            f'{self._center_latitude + offset},{self._center_longitude + long_scale * offset}|'
            f'{self._center_latitude + offset},{self._center_longitude - long_scale * offset}|'
            f'{self._center_latitude - offset},{self._center_longitude + long_scale * offset}|'
            f'{self._center_latitude - offset},{self._center_longitude - long_scale * offset}'
        )

        print(f'Marker coords {r}')
        return r

    def deg_lat_per_foot(self):
        return 1/(12000*5280/90)

class LatLongToPixelConverter:
    '''For maps returned by google static maps api returns converts latitude and longitude
       degree spans into pixels for various scales and zooms.'''

    # Derived empirically by placing and measuring markers on map.
    # Zoom21-Scale1-Lat_height=0.0003125-Long_width=0.00040625.png
    LATITUDE = 37.386197
    LONGITUDE = -122.110088

    LATITUDE_HEIGHT_DEG = 'latitude_height_deg'
    LONGITUDE_WIDTH_DEG = 'longitude_width_deg'
    LATITUDE_HEIGHT_PIXELS = 'latitude_height_pixels'
    LONGITUDE_WIDTH_PIXELS = 'longitude_width_pixels'

    EMPIRICAL_MAP_RESOLUTIONS = {
        21: { #zoom
            LATITUDE_HEIGHT_DEG: 0.0003125,
            LONGITUDE_WIDTH_DEG: 0.00040625,
            LATITUDE_HEIGHT_PIXELS: 586,
            LONGITUDE_WIDTH_PIXELS: 606,
        },
        20: {
            LATITUDE_HEIGHT_DEG: 0.000625,
            LONGITUDE_WIDTH_DEG: 0.0008125,
            LATITUDE_HEIGHT_PIXELS: 586,
        },
        19: {
            LATITUDE_HEIGHT_DEG: 0.0009375,
            LONGITUDE_WIDTH_DEG: 0.0012875,
            LATITUDE_HEIGHT_PIXELS: 440,
        },
        18: {
            LATITUDE_HEIGHT_DEG: 0.00125,
            LONGITUDE_WIDTH_DEG: 0.001625,
            LATITUDE_HEIGHT_PIXELS: 295,
        },
        17: {
            LATITUDE_HEIGHT_DEG: 0.00390625,
            LONGITUDE_WIDTH_DEG: 0.005078125,
            LATITUDE_HEIGHT_PIXELS: 459,
        },
    }

    def get_latitude_deg_per_pixel(self, zoom, scale) -> float:
        zoom = int(zoom)
        scale = int(scale)

        assert scale == 1 or scale == 2, 'scale must be 1 or 2'

        data_for_zoom = self.__class__.EMPIRICAL_MAP_RESOLUTIONS[zoom]
        lpp = data_for_zoom[self.__class__.LATITUDE_HEIGHT_DEG] / \
              data_for_zoom[self.__class__.LATITUDE_HEIGHT_PIXELS]

        if scale == 2:
            lpp = lpp / 2

        return lpp

    def get_longitude_deg_per_pixel(self, latitude_deg, zoom, scale):
        return self._long_vs_lat_scale_factor(latitude_deg) * self.get_latitude_deg_per_pixel(zoom, scale) # pylint: disable=C0301

    def _long_vs_lat_scale_factor(self, latitude_deg):
        return 1 / math.cos(math.radians(latitude_deg))

    def deg_latitude_per_foot(self):
        return 1/(12000*5280/90)

    def deg_longitude_per_foot(self, latitude):
        return self._long_vs_lat_scale_factor(latitude) * self.deg_latitude_per_foot()

    def get_info(self):
        return {zoom: self.get_latitude_deg_per_pixel(zoom, 1)
                for zoom in self.__class__.EMPIRICAL_MAP_RESOLUTIONS}

class MapFitter:
    '''Given a longitude series and latitude series returns a map that
       fits the points with a border in feet.'''
    # From google static maps api.
    MAX_MAP_HEIGHT_PIXELS = 640
    MAX_MAP_WIDTH_PIXELS = 640
    MIN_DIMENSION = 600

    def __init__(self,
                 latitude_series,
                 longitude_series,
                 border_feet=10,
                 add_markers=False,
                ):
        self._latitude_series = np.array(latitude_series)
        self._longitude_series = np.array(longitude_series)
        self._border_feet = border_feet
        self._add_markers = add_markers

        # lazy init
        self._zoom_to_fit = None

    def get_center_latitude(self):
        return 0.5 * (self._get_max_latitude() + self._get_min_latitude())

    def get_center_longitude(self):
        return 0.5 * (self._get_max_longitude() + self._get_min_longitude())

    def _get_max_latitude(self):
        return np.max(self._latitude_series)

    def _get_min_latitude(self):
        return np.min(self._latitude_series)

    def _get_max_longitude(self):
        return np.max(self._longitude_series)

    def _get_min_longitude(self):
        return np.min(self._longitude_series)

    def _get_max_map_latitude_extent(self, zoom):
        return self.__class__.MAX_MAP_HEIGHT_PIXELS * \
               LatLongToPixelConverter().get_latitude_deg_per_pixel(zoom, 1)

    def _get_max_map_longitude_extent(self, zoom):
        return self.__class__.MAX_MAP_WIDTH_PIXELS * \
               LatLongToPixelConverter().get_longitude_deg_per_pixel(self.get_center_latitude(),
                                                                     zoom,
                                                                     1,
                                                                    )

    def _get_border_long_deg(self):
        return self._border_feet * \
               LatLongToPixelConverter().deg_longitude_per_foot(self.get_center_latitude())

    def _get_border_lat_deg(self):
        return self._border_feet * \
               LatLongToPixelConverter().deg_latitude_per_foot()

    def _get_data_longitude_extent(self):
        return abs(self._get_max_longitude() - self._get_min_longitude()) +\
               2 * self._get_border_long_deg()

    def _get_data_latitude_extent(self):
        return abs(self._get_max_latitude() - self._get_min_latitude()) +\
               2 * self._get_border_lat_deg()

    def _get_zoom_to_fit(self):
        if self._zoom_to_fit is None:
            lat_extent = self._get_data_latitude_extent()
            long_extent = self._get_data_longitude_extent()

            zooms = list(range(22))
            zooms.reverse()
            for zoom in zooms:
                if self._get_max_map_latitude_extent(zoom) > lat_extent and \
                   self._get_max_map_longitude_extent(zoom) > long_extent:

                    self._zoom_to_fit = zoom
                    return self._zoom_to_fit

            assert True, 'Error: no zoom_to_fit found'

        return self._zoom_to_fit

    def get_zoom(self):
        return self._get_zoom_to_fit()

    def _get_map_width_pixels(self):
        return int(self.__class__.MAX_MAP_WIDTH_PIXELS * \
               (self._get_data_longitude_extent() / self._get_max_map_longitude_extent(self._get_zoom_to_fit()))) # pylint: disable=C0301

    def _get_map_height_pixels(self):
        return int(self.__class__.MAX_MAP_HEIGHT_PIXELS * \
               (self._get_data_latitude_extent() / self._get_max_map_latitude_extent(self._get_zoom_to_fit()))) # pylint: disable=C0301

    def get_latitude_series(self):
        return self._latitude_series

    def get_longitude_series(self):
        return self._longitude_series

    def get_scale(self):
        if self._get_map_width_pixels() < self.__class__.MIN_DIMENSION and \
           self._get_map_height_pixels() < self.__class__.MIN_DIMENSION:
            return 2
        return 1

    def get_map(self):
        return GeoMapper(center_latitude=self.get_center_latitude(),
                         center_longitude=self.get_center_longitude(),
                         size=f'{self._get_map_width_pixels()}x{self._get_map_height_pixels()}',
                         zoom=self._get_zoom_to_fit(),
                         scale=self.get_scale(),
                         add_markers=self._add_markers,
                        ).get_map()

    def get_map_scaled_width(self):
        return self.get_scale() * self._get_map_width_pixels()

    def get_map_scaled_height(self):
        return self.get_scale() * self._get_map_height_pixels()


class MapCoordinateTransformer:
    '''Transforms latitude longitude coordinates to tkinter canvas coordinates.
       Assumes the canvas is sized to fit the map exactly. x is longitude. y
       is latituded. x=0, y=0 is top left of map image. y increases downwards.'''

    def __init__(self,
                 center_latitude,
                 center_longitude,
                 width_pixels,
                 height_pixels,
                 zoom,
                 scale,
                ):
        self._center_latitude = center_latitude
        self._center_longitude = center_longitude
        self._width_pixels = width_pixels
        self._height_pixels = height_pixels
        self._zoom = zoom
        self._scale = scale

        # lazy init
        self._lat_deg_per_px = None
        self._long_deg_per_px = None
        self._lat_top = None
        self._long_left = None


    def get_x_y_for_lat_long(self, latitude_deg, longitude_deg):
        return (self.get_x_for_longitude(longitude_deg), self.get_y_for_latitude(latitude_deg))

    def get_y_for_latitude(self, latitude_deg):
        lat_diff = self._get_lat_of_top() - latitude_deg
        return int(round(lat_diff / self._get_lat_deg_per_px()))

    def get_x_for_longitude(self, longitude_deg):
        long_diff = longitude_deg - self._get_long_of_left()
        return int(round(long_diff / self._get_long_deg_per_px()))

    def _get_lat_deg_per_px(self):
        if self._lat_deg_per_px is None:
            self._lat_deg_per_px = LatLongToPixelConverter().get_latitude_deg_per_pixel(self._zoom,
                                                                                        self._scale,
                                                                                        )
        return self._lat_deg_per_px

    def _get_long_deg_per_px(self):
        if self._long_deg_per_px is None:
            self._long_deg_per_px =\
                LatLongToPixelConverter().get_longitude_deg_per_pixel(self._center_latitude,
                                                                      self._zoom,
                                                                      self._scale,
                                                                     )
        return self._long_deg_per_px

    def _get_long_of_left(self):
        if self._long_left is None:
            px_from_center = self._width_pixels / 2
            angle_from_center = self._get_long_deg_per_px() * px_from_center
            self._long_left = self._center_longitude - angle_from_center
        return self._long_left

    def _get_lat_of_top(self):
        if self._lat_top is None:
            px_from_center = self._height_pixels / 2
            angle_from_center = self._get_lat_deg_per_px() * px_from_center
            self._lat_top = self._center_latitude + angle_from_center
        return self._lat_top
