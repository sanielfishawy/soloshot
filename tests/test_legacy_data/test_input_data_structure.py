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
        'base_tilt_at_current_pan_angle',
        'base_roll_at_current_pan_angle',
        'cam_pitch',
        'base_compass',
    ]

    LENS_TIME_FIELD = 'lens_time'

    LENS_NPZ_FIELDS = [
        LENS_TIME_FIELD,
        'lens_fov',
        'lens_zoom',
    ]

    TAG_TIME_FIELD = 'tag_time'

    TAG_NPZ_FIELDS = [
        TAG_TIME_FIELD,
        'tag_latitude',
        'tag_longitude',
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
        for npz_file_path in self.get_all_npz_file_paths():
            np_data = np.load(npz_file_path)
            actual_npz_fields = np_data.files
            name_of_first_field = actual_npz_fields[0]
            length_of_first_field = np_data[name_of_first_field].size
            self.assertGreater(length_of_first_field,
                               0,
                               msg=(f'{name_of_first_field} in {npz_file_path} '
                                    f'is too short ({length_of_first_field}).'
                                   )
                               )
            for actual_field in actual_npz_fields:
                field_len = np_data[actual_field].size
                self.assertEqual(field_len,
                                 length_of_first_field,
                                 msg=(f'{actual_field} ({field_len}) '
                                      f'not same length as {name_of_first_field} ({length_of_first_field}) '
                                      f'in {npz_file_path}'
                                     )
                                 )

    def test_non_implemented_fields_are_full_of_nones(self):
        for npz_file_path in self.get_all_npz_file_paths():
            np_data = np.load(npz_file_path)
            for field in np_data.files:
                if field in self.__class__.UNIMPLEMENTED_FIELDS:
                    field_data = np_data[field]
                    if field_data.size == 0:
                        self.fail(f'Apparent unimplemented field: {field} in {npz_file_path} is empty')
                    if (field_data != None).all(): # pylint: disable=C0121
                        self.fail(f'Apparent unimplemented field: {field} in {npz_file_path} not full of Nones')

    def test_implemented_fields_have_no_nones(self):
        for npz_file_path in self.get_all_npz_file_paths():
            np_data = np.load(npz_file_path)
            for field in np_data.files:
                if field not in self.__class__.UNIMPLEMENTED_FIELDS:
                    field_data = np_data[field]
                    if field_data.size == 0:
                        self.fail(f'Apparent implemented field: {field} in {npz_file_path} is empty')
                    if (field_data == None).any(): # pylint: disable=C0121
                        self.fail(f'Apparent implemented field: {field} in {npz_file_path} has a None')

    def test_video_file_can_be_opened_with_cv2(self):
        for video_path in self.get_video_paths():
            if not cv2.VideoCapture(str(video_path.resolve())).isOpened():
                self.fail(f'Could not open {video_path} with cv2.VideoCapture')

    def test_time_fields_duration_same_as_video_duration(self):
        for session_dir in self.get_session_dirs():
            video_path = self.get_video_path(session_dir)
            assert video_path is not None,\
                   (f'No video found in {session_dir.name} '
                    f'cannot run {self.test_time_fields_duration_same_as_video_duration.__name__}')
            video_duration = self.get_duration_ms_of_video_at_path(video_path)

            for npz_path in self.get_npz_file_paths(session_dir):
                npz_duration = self.get_duration_in_ms_for_npz_with_a_time_field(npz_path)
                if npz_duration is None:
                    continue
                delta = 200
                self.assertAlmostEqual(video_duration,
                                       npz_duration,
                                       delta=delta,
                                       msg=(f'{session_dir.name}: video duration: ({video_duration}) '
                                            f'not within {delta} ms of '
                                            f'{npz_path.name} timefield duration ({npz_duration})'
                                           )
                                       )

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

    def get_npz_file_paths(self, session_dir):
        return [session_dir / self.__class__.NPZ_DIR / npz_filename
                for npz_filename in self.get_npz_filenames()]

    def get_all_npz_file_paths(self):
        r = []
        for session_dir in self.get_session_dirs():
            r += self.get_npz_file_paths(session_dir)
        return r

    def get_video_paths(self):
        return [list(track_dir.glob(self.__class__.RECODED_VIDEO_FILE))[0]
                for track_dir in self.get_track_dirs()
                if len(list(track_dir.glob(self.__class__.RECODED_VIDEO_FILE))) > 0]

    def get_video_path(self, session_dir):
        video_files = list(self.get_track_dir(session_dir).glob(self.__class__.RECODED_VIDEO_FILE))
        if len(video_files) == 0:
            return None
        return video_files[0]

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

    def get_duration_in_ms_for_npz_with_a_time_field(self, npz_path):
        npz_data = np.load(npz_path)
        time_fields = [field for field in npz_data.files
                       if field in self.__class__.TIME_FIELDS]
        if not time_fields:
            return None
        time_data = npz_data[time_fields[0]]
        return time_data[-1] - time_data[0]


if __name__ == '__main__':
    unittest.main()
