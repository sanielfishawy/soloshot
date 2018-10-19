# pylint: disable=C0301, C0413
import os
import sys
import unittest
from pathlib import Path
import numpy as np
import cv2
sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.legacy_data_file_system_helper import LegacyDataFileSystemHelper as LDFH

class TestInputDataStructure(unittest.TestCase):
    '''Verifies that the legacy data files are in the expected directory structure and
    contain the expected data. Currently the head of the file heirarchy is the
    SESSION_DB folder'''

    # Change this to the path containing the SESSION_DB folder
    HEAD_PATH = Path('/Volumes/WD')

    def setUp(self):
        self.ldfh = LDFH(self.__class__.HEAD_PATH)

    def test_top_level_dir_exists(self):
        self.assertTrue(self.ldfh.get_top_level_dir_path().exists())

    def test_at_least_one_session_dir_exists(self):
        try:
            num_session_dirs = sum(1 for _ in self.ldfh.get_session_dirs())
            self.assertGreater(num_session_dirs, 0)
        except FileNotFoundError:
            self.fail('Top level dir not found')

    def test_all_children_of_top_level_dir_are_dirs(self):
        try:
            for session_dir in self.ldfh.get_session_dirs():
                self.assertTrue(session_dir.is_dir())
        except FileNotFoundError:
            self.fail('Top level dir not found')

    def test_directory_structure_correct(self):
        for session_dir_path in self.ldfh.get_session_dirs():
            self.verify_directory_and_sub_directories(LDFH.DIRECTORY_STRUCTURE,
                                                      session_dir_path,
                                                     )

    def test_no_extra_files_in_npz_dirs(self):
        for session_dir_path in self.ldfh.get_session_dirs():
            npz_dir = session_dir_path / LDFH.NPZ_DIR
            for p_path in npz_dir.iterdir():
                if not p_path.name in LDFH.DIRECTORY_STRUCTURE[LDFH.NPZ_DIR]:
                    if '.DS_Store' not in p_path.name:
                        self.fail(f'Extra NPZ file: {p_path}')

    def test_npz_fields_exist_with_no_extras(self):
        for session_dir_path in self.ldfh.get_session_dirs():
            for npz_file, expected_npz_fields in LDFH.NPZ_FIELDS.items():
                npz_file_path = session_dir_path / LDFH.NPZ_DIR / npz_file
                actual_npz_fields = np.load(npz_file_path).files
                for expected_field in expected_npz_fields:
                    if expected_field not in actual_npz_fields:
                        self.fail(f'No {expected_field} in {npz_file_path}')
                for actual_field in actual_npz_fields:
                    if actual_field not in expected_npz_fields:
                        self.fail(f'Extra field: {actual_field} in {npz_file_path}')

    def test_npz_fields_have_the_same_length(self):
        for npz_file_path in self.ldfh.get_all_npz_file_paths():
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
        for npz_file_path in self.ldfh.get_all_npz_file_paths():
            np_data = np.load(npz_file_path)
            for field in np_data.files:
                if field in LDFH.UNIMPLEMENTED_FIELDS:
                    field_data = np_data[field]
                    if field_data.size == 0:
                        self.fail(f'Apparent unimplemented field: {field} in {npz_file_path} is empty')
                    if (field_data != None).all(): # pylint: disable=C0121
                        self.fail(f'Apparent unimplemented field: {field} in {npz_file_path} not full of Nones')

    def test_implemented_fields_have_no_nones(self):
        for npz_file_path in self.ldfh.get_all_npz_file_paths():
            np_data = np.load(npz_file_path)
            for field in np_data.files:
                if field not in LDFH.UNIMPLEMENTED_FIELDS:
                    field_data = np_data[field]
                    if field_data.size == 0:
                        self.fail(f'Apparent implemented field: {field} in {npz_file_path} is empty')
                    if (field_data == None).any(): # pylint: disable=C0121
                        self.fail(f'Apparent implemented field: {field} in {npz_file_path} has a None')

    def test_video_file_can_be_opened_with_cv2(self):
        for video_path in self.ldfh.get_video_paths():
            if not cv2.VideoCapture(str(video_path.resolve())).isOpened():
                self.fail(f'Could not open {video_path} with cv2.VideoCapture')

    def test_time_fields_duration_same_as_video_duration(self):
        for session_dir in self.ldfh.get_session_dirs():
            video_path = self.ldfh.get_video_path(session_dir)
            assert video_path is not None,\
                   (f'No video found in {session_dir.name} '
                    f'cannot run {self.test_time_fields_duration_same_as_video_duration.__name__}')
            video_duration = self.ldfh.get_duration_ms_of_video_at_path(video_path)

            for npz_path in self.ldfh.get_npz_file_paths(session_dir):
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

    def test_all_time_fields_monotonically_asscend(self):
        for session_dir in self.ldfh.get_session_dirs():
            for field, data in self.ldfh.get_npz_time_fields(session_dir).items():
                self.assertTrue(self.field_is_monotonically_increasing(data),
                                msg=(f'{session_dir.name}: '
                                     f'{field} is not monotonically increasing.'
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
        if num_wilds > 1 and dir_or_file_with_wild_chars not in LDFH.MULTIPLE_MATCHING_FILES_ALLOWED:
            self.fail(f'Too many {path / dir_or_file_with_wild_chars} found.')
        for wild in wilds:
            self.assertTrue((path /  wild).exists())

    def get_duration_ms_of_video_at_path(self, video_path):
        cap = cv2.VideoCapture(str(video_path.resolve()))
        if not cap.isOpened():
            return 0
        cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
        return cap.get(cv2.CAP_PROP_POS_MSEC)

    def get_duration_in_ms_for_npz_with_a_time_field(self, npz_path):
        npz_data = np.load(npz_path)
        time_fields = [field for field in npz_data.files
                       if field in LDFH.TIME_FIELDS]
        if not time_fields:
            return None
        time_data = npz_data[time_fields[0]]
        return time_data[-1] - time_data[0]

    def field_is_monotonically_increasing(self, data):
        return np.all(np.diff(data) >= 0)

if __name__ == '__main__':
    unittest.main()
