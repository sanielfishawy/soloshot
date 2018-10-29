from pathlib import Path
import shutil
import urllib
import math
import requests
import yaml

class GeoMapper:

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
        self._zoom = str(zoom)
        self._size = size
        self._maptype = maptype
        self._scale = str(scale)

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
               f'Gota non 200 status ({r.status_code}) from http request for google maps.'

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
        if self._zoom == '20':
            offset = 2 * offset

        print(f'Center latitude = {self._center_latitude}')
        print(f'Center longitude = {self._center_longitude}')
        print(f'Offset = {offset}')
        print(f'Latitude height = {2 * offset}')
        print(f'Longitude width = {2 * (long_scale * offset)}')

        r = (
            f'{self._center_latitude},{self._center_longitude}|'
            f'{self._center_latitude + offset},{self._center_longitude + long_scale * offset}|'
            f'{self._center_latitude + offset},{self._center_longitude - long_scale * offset}|'
            f'{self._center_latitude - offset},{self._center_longitude + long_scale * offset}|'
            f'{self._center_latitude - offset},{self._center_longitude - long_scale * offset}'
        )

        print(f'Marker coords{r}')
        return r


    def deg_lat_per_foot(self):
        return 1/(12000*5280/90)

class LatLongToPixelConverter:

    # Derived empirically by placing and measuring markers on map.
    # Zoom21-Scale1-Lat_height=0.0003125-Long_width=0.00040625.png
    LATITUDE = 37.386197
    LONGITUDE = -122.110088
    LATITUDE_HEIGHT_DEG = 0.0003125
    LONGITUDE_WIDTH_DEG = 0.00040625
    LATITUDE_HEIGHT_PIXELS = 586
    LONGITUDE_WIDTH_PIXELS = 606

    def get_latitude_deg_per_pixel(self, zoom, scale) -> float:
        zoom = int(zoom)
        scale = int(scale)

        assert scale == 1 or scale == 2, 'scale must be 1 or 2'

        lpp = self.__class__.LATITUDE_HEIGHT_DEG / self.__class__.LATITUDE_HEIGHT_PIXELS

        if scale == 2:
            lpp = lpp / 2

        return (22 - zoom) * lpp

    def get_longitude_deg_per_pixel(self, latitude_deg, zoom, scale):
        return self._long_vs_lat_scale_factor(latitude_deg) * self.get_latitude_deg_per_pixel(zoom, scale) # pylint: disable=C0301

    def _long_vs_lat_scale_factor(self, latitude_deg):
        return 1 / math.cos(math.radians(latitude_deg))
