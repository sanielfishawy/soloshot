# pylint: disable=C0301
import os
import sys
import unittest
from pathlib import Path
import numpy as np
import cv2
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
    RAW_VIDEO_FILE = '*.MP4'
    RECODED_VIDEO_FILE = 'video.mp4'
    SESSION_FILE = 'SS3_EDIT_*.SESSION'

    NPZ_DIR = 'NPZ'
    BASE_NPZ_FILE = 'base.npz'
    LENS_NPZ_FILE = 'lens.npz'
    TAG_NPZ_FILE = 'tag.npz'
    CAMERA_NPZ_FILE = 'camera.npz'

    BASE_TIME_FIELD = 'base_time'

    BASE_NPZ_FIELDS = [
        BASE_TIME_FIELD,
        'pan_motor_read',
        'tilt_motor_read',
        'base_latitude',
        'base_longitude',
        'base_altitude_gps',
        'base_altitude_barometer',
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
            RAW_VIDEO_FILE,
            RECODED_VIDEO_FILE,
            SESSION_FILE,
        ]
    }

    MULTIPLE_MATCHING_FILES_ALLOWED = [
        RAW_VIDEO_FILE,
    ]

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
                    if '.DS_Store' not in p_path.name:
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

    def test_npz_fields_have_the_same_length(self):
        for npz_file_path in self.get_npz_file_paths():
            np_data = np.load(npz_file_path)
            actual_npz_fields = np_data.files
            name_of_first_field = actual_npz_fields[0]
            length_of_first_field = len(np_data[name_of_first_field])
            if length_of_first_field < 1:
                self.fail(f'{name_of_first_field} in {npz_file_path} is too short. ({length_of_first_field}')
            for actual_field in actual_npz_fields:
                field_len = len(np_data[actual_field])
                if field_len != length_of_first_field:
                    self.fail(f'{actual_field} ({field_len}) not same length as {name_of_first_field} ({length_of_first_field}) in {npz_file_path}')

    def test_non_implemented_fields_are_full_of_nones(self):
        for npz_file_path in self.get_npz_file_paths():
            np_data = np.load(npz_file_path)
            for field in np_data.files:
                field_data = np_data[field]
                if len(field_data) == 1:
                    continue
                if (field_data == field_data[0]).all():
                    if (field_data != None).all(): # pylint: disable=C0121
                        self.fail(f'Apparent unimplemented field: {field} in {npz_file_path} not full of Nones')

    def test_video_file_can_be_opened_with_cv2(self):
        for video_path in self.get_video_paths():
            if not cv2.VideoCapture(str(video_path.resolve())).isOpened():
                self.fail(f'Could not open {video_path} with cv2.VideoCapture')

    def test_video_duration_same_as_base_duration(self):
        for session_dir in self.get_session_dirs():
            self.assertAlmostEqual(self.get_duration_ms_base_npz(self.get_base_npz_path(session_dir)),
                                   self.get_duration_ms_of_video_at_path(self.get_video_path(session_dir)))

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
        if num_wilds > 1 and dir_or_file_with_wild_chars not in self.__class__.MULTIPLE_MATCHING_FILES_ALLOWED:
            self.fail(f'Too many {path / dir_or_file_with_wild_chars} found.')
        for wild in wilds:
            self.assertTrue((path /  wild).exists())

    def get_session_dirs(self):
        r = list(self.__class__.TOP_LEVEL_DIR_PATH.iterdir())
        return [directory for directory in r if 'DS_Store' not in directory.name]

    def get_npz_filenames(self):
        return self.__class__.NPZ_FIELDS.keys()

    def get_npz_file_paths(self):
        r = []
        for session_dir in self.get_session_dirs():
            for npz_filename in self.get_npz_filenames():
                r.append(session_dir / self.__class__.NPZ_DIR / npz_filename)
        return r

    def get_video_paths(self):
        return [list(track_dir.glob(self.__class__.RECODED_VIDEO_FILE))[0]
                for track_dir in self.get_track_dirs()
                if len(list(track_dir.glob(self.__class__.RECODED_VIDEO_FILE))) > 0]

    def get_video_path(self, session_dir):
        return list(self.get_track_dir(session_dir).glob(self.__class__.RECODED_VIDEO_FILE))[0]


    def get_track_dirs(self):
        return [self.get_track_dir(session_dir) for session_dir in self.get_session_dirs()]

    def get_track_dir(self, session_dir):
        return list(session_dir.glob(self.__class__.TRACK_DIR))[0]

    def get_duration_ms_of_video_at_path(self, video_path):
        cap = cv2.VideoCapture(str(video_path.resolve()))
        if not cap.isOpened():
            return 0
        cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
        return cap.get(cv2.CAP_PROP_POS_MSEC)

    def get_duration_ms_base_npz(self, base_path):
        base_time = np.load(base_path)[self.__class__.BASE_TIME_FIELD]
        return base_time[-1] - base_time[0]

    def get_base_npz_path(self, session_dir):
        return session_dir / self.__class__.NPZ_DIR / self.__class__.BASE_NPZ_FILE

if __name__ == '__main__':
    unittest.main()
