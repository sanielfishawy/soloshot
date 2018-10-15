# pylint: disable=C0301
import os
import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0, os.getcwd())

class TestInputDataStructure(unittest.TestCase):
    '''Verifies that the legacy data files are in the expected directory structure and
    contain the expected data. Currently the head of the file heirarchy is the
    SESSION_DB folder'''

    # Change this to the path containing the SESSION_DB folder
    HEAD_PATH = Path('/Volumes/WD')

    TOP_LEVEL_DIR = 'SESSION_DB'
    TOP_LEVEL_DIR_PATH = HEAD_PATH / TOP_LEVEL_DIR

    SESSION_DIR = '*'

    TRACK_DIR = 'Track*'
    VIDEO_FILE = '*.MP4'
    SESSION_FILE = 'SS3_EDIT_*.SESSION'

    NPZ_DIR = 'NPZ'
    BASE_NPZ_FILE = 'base.npz'
    LENS_NPZ_FILE = 'lens.npz'
    TAG_NPZ_FILE = 'tag.npz'
    CAMERA_NPZ_FILE = 'camera.npz'

    BASE_NPZ_FIELDS = [
        'base_time',
        'pan_motor_read',
        'tilt_motor_read',
        'base_lat',
        'base_long',
        'base_alt_gps',
        'base_alt_barometer',
        'base_tilt_at_current_pan_angle',
        'base_roll_at_current_pan_angle',
        'cam_pitch',
        'base_compass',
    ]

    LENS_NPZ_FIELDS = [
        'lens_time',
        'lens_fov',
        'lens_zoom',
    ]

    TAG_NPZ_FIELDS = [
        'tag_time',
        'tag_latitude',
        'tag_longitude',
        'tag_altitude_gps',
        'tag_altitude_barometer',
    ]

    CAMERA_NPZ_FIELDS = [
        'record_start_time',
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
            VIDEO_FILE,
            SESSION_FILE,
        ]
    }

    def setUp(self):
        pass

    def test_top_level_dir_exists(self):
        self.assertTrue(self.__class__.TOP_LEVEL_DIR_PATH.exists())

    def test_at_least_one_session_dir_exists(self):
        try:
            num_session_dirs = sum(1 for _ in self.get_session_dirs())
            self.assertGreater(num_session_dirs, 0)
        except FileNotFoundError:
            self.fail('Top level dir not found')

    def test_all_children_of_top_level_dir_are_dirs(self):
        try:
            for session_dir in self.get_session_dirs():
                self.assertTrue(session_dir.is_dir())
        except FileNotFoundError:
            self.fail('Top level dir not found')

    def test_directory_structure_correct(self):
        for session_dir_path in self.get_session_dirs():
            self.verify_directory_and_sub_directories(self.__class__.DIRECTORY_STRUCTURE,
                                                      session_dir_path,
                                                     )

    def test_no_extra_files_in_npz_dirs(self):
        for session_dir_path in self.get_session_dirs():
            npz_dir = session_dir_path / self.__class__.NPZ_DIR
            for p_path in npz_dir.iterdir():
                if not p_path.name in self.__class__.DIRECTORY_STRUCTURE[self.__class__.NPZ_DIR]:
                    if p_path.name != '_DS_Store':
                        self.fail(f'Extra NPZ file: {p_path}')

    def test_npz_fields_exist_with_no_extras(self):
        for session_dir_path in self.get_session_dirs():
            for npz_file, expected_npz_fields in self.__class__.NPZ_FIELDS.items():
                npz_file_path = session_dir_path / self.__class__.NPZ_DIR / npz_file
                actual_npz_fields = np.load(npz_file_path).files
                for expected_field in expected_npz_fields:
                    if expected_field not in actual_npz_fields:
                        self.fail(f'No {expected_field} in {npz_file_path}')
                for actual_field in actual_npz_fields:
                    if actual_field not in expected_npz_fields:
                        self.fail(f'Extra field: {actual_field} in {npz_file_path}')

    def verify_directory_and_sub_directories(self, dir_structure, path: Path):
        if isinstance(dir_structure, dict):
            for child in dir_structure.keys():
                self.verify_wild_path_exists(path, child)
                for wild in path.glob(child):
                    self.verify_directory_and_sub_directories(dir_structure[child], path / wild)
        elif isinstance(dir_structure, list):
            for filename in dir_structure:
                self.verify_wild_path_exists(path, filename)

    def verify_wild_path_exists(self, path, dir_or_file_with_wild_chars):
        wilds = path.glob(dir_or_file_with_wild_chars)
        num_wilds = sum(1 for _ in wilds)
        if num_wilds < 1:
            self.fail(f'{path / dir_or_file_with_wild_chars} not found.')
        if num_wilds > 1:
            self.fail(f'Too many {path / dir_or_file_with_wild_chars} found.')
        for wild in wilds:
            self.assertTrue((path /  wild).exists())

    def get_session_dirs(self):
        return self.__class__.TOP_LEVEL_DIR_PATH.iterdir()

if __name__ == '__main__':
    unittest.main()
