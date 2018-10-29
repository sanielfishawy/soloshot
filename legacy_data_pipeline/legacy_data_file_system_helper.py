# pylint: disable=C0301
import os
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, os.getcwd())

class LegacyDataFileSystemHelper:
    '''For navigating the legacy data filesystem'''

    TOP_LEVEL_DIR = 'SESSION_DB'

    SESSION_DIR = '*'

    TRACK_DIR = 'Track*'
    RAW_VIDEO_FILE = '*.MP4'
    RECODED_VIDEO_FILE = 'video.mp4'
    SESSION_FILE = 'SS3_EDIT_*.SESSION'

    NPZ_DIR = 'NPZ'
    BASE_NPZ_FILE = 'base.npz'
    LENS_NPZ_FILE = 'lens.npz'
    TAG_NPZ_FILE = 'tag.npz'
    CAMERA_NPZ_FILE = 'camera.npz'

    BASE_TIME_FIELD = 'base_time'
    PAN_MOTOR_READ_FIELD = 'pan_motor_read'

    BASE_NPZ_FIELDS = [
        BASE_TIME_FIELD,
        PAN_MOTOR_READ_FIELD,
        'tilt_motor_read',
        'base_tilt_at_current_pan_angle',
        'base_roll_at_current_pan_angle',
        'cam_pitch',
        'base_compass',
    ]

    LENS_TIME_FIELD = 'lens_time'
    LENS_FOV_FIELD = 'lens_fov'

    LENS_NPZ_FIELDS = [
        LENS_TIME_FIELD,
        LENS_FOV_FIELD,
        'lens_zoom',
    ]

    TAG_TIME_FIELD = 'tag_time'
    TAG_LATITUDE_FIELD = 'tag_latitude'
    TAG_LONGITUDE_FIELD = 'tag_longitude'

    TAG_NPZ_FIELDS = [
        TAG_TIME_FIELD,
        TAG_LATITUDE_FIELD,
        TAG_LONGITUDE_FIELD,
        'tag_acceleration',
        'tag_altitude_gps',
        'tag_altitude_barometer',
        'base_latitude',
        'base_longitude',
        'base_altitude_gps',
        'base_altitude_barometer',
    ]

    CAMERA_NPZ_FIELDS = [
        'record_start_time',
        'preview_start_time',
    ]

    TIME_FIELDS = [
        BASE_TIME_FIELD,
        LENS_TIME_FIELD,
        TAG_TIME_FIELD,
    ]

    UNIMPLEMENTED_FIELDS = [
        'base_altitude_barometer',
        'base_compass',
        'lens_zoom',
        'tag_altitude_barometer',
        'preview_start_time',
    ]

    NPZ_FIELDS = {
        BASE_NPZ_FILE: BASE_NPZ_FIELDS,
        LENS_NPZ_FILE: LENS_NPZ_FIELDS,
        TAG_NPZ_FILE: TAG_NPZ_FIELDS,
        CAMERA_NPZ_FILE: CAMERA_NPZ_FIELDS,
    }

    DIRECTORY_STRUCTURE = {
        NPZ_DIR: [
            BASE_NPZ_FILE,
            LENS_NPZ_FILE,
            TAG_NPZ_FILE,
            CAMERA_NPZ_FILE,
        ],
        TRACK_DIR: [
            RAW_VIDEO_FILE,
            RECODED_VIDEO_FILE,
            SESSION_FILE,
        ]
    }

    MULTIPLE_MATCHING_FILES_ALLOWED = [
        RAW_VIDEO_FILE,
    ]

    def __init__(self, head_path: Path):
        self.head_path = head_path
        self.top_level_dir_path = self.head_path / self.__class__.TOP_LEVEL_DIR

    def get_top_level_dir_path(self):
        return self.top_level_dir_path

    def get_session_dirs(self):
        r = list(self.top_level_dir_path.iterdir())
        return [directory for directory in r if 'DS_Store' not in directory.name]

    def get_session_dir_path(self, session_dir_name):
        return self.top_level_dir_path / session_dir_name

    def get_npz_dir_path(self, session_dir_name):
        return self.get_session_dir_path(session_dir_name) / self.__class__.NPZ_DIR

    def get_npz_file_path(self, session_dir_name, filename):
        return self.get_npz_dir_path(session_dir_name) / filename

    def get_field_from_npz_file(self, session_dir_name, filename, fieldname):
        return np.load(self.get_npz_file_path(session_dir_name, filename))[fieldname]

    def get_npz_filenames(self):
        return self.__class__.NPZ_FIELDS.keys()

    def get_npz_file_paths(self, session_dir_name):
        return [self.get_npz_dir_path(session_dir_name) / npz_filename
                for npz_filename in self.get_npz_filenames()]

    def get_npz_fields(self, session_dir_name):
        r = {}
        for npz_file_path in self.get_npz_file_paths(session_dir_name):
            npz_data = np.load(npz_file_path)
            for field in npz_data.files:
                r[field] = npz_data[field]
        return r

    def get_npz_time_fields(self, session_dir_name):
        all_npz_fields = self.get_npz_fields(session_dir_name)
        return {key: all_npz_fields[key]
                for key in all_npz_fields.keys() # pylint: disable=C0201
                if key in self.__class__.TIME_FIELDS}

    def get_all_npz_file_paths(self):
        r = []
        for session_dir_name in self.get_session_dirs():
            r += self.get_npz_file_paths(session_dir_name)
        return r

    def get_video_paths(self):
        return [list(track_dir.glob(self.__class__.RECODED_VIDEO_FILE))[0]
                for track_dir in self.get_track_dirs()
                if len(list(track_dir.glob(self.__class__.RECODED_VIDEO_FILE))) > 0]

    def get_video_path(self, session_dir):
        video_files = list(self.get_track_dir(session_dir).glob(self.__class__.RECODED_VIDEO_FILE))
        if not video_files:
            return None
        return video_files[0]

    def get_track_dirs(self):
        return [self.get_track_dir(self.get_session_dir_path(session_dir_name))
                for session_dir_name
                in self.get_session_dirs()
               ]

    def get_track_dir(self, session_dir_name):
        return list(self.get_session_dir_path(session_dir_name).glob(self.__class__.TRACK_DIR))[0]
