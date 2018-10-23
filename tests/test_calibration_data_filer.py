# pylint: disable=C0413, W0212
import sys
import os
import unittest
from pathlib import Path

sys.path.insert(0, os.getcwd())
from legacy_data_pipeline.calibration_data_filer import CalibrationDataFiler

class TestCalibrationDataFiler(unittest.TestCase):
    TOP_LEVEL_PATH = Path('.') / 'data/test_data/test_calibration_data'
    DATA_DIR_NAME = 'test_session_calibration_data'
    DATA_DIR_PATH = TOP_LEVEL_PATH / DATA_DIR_NAME
    DATA_FILENAME = CalibrationDataFiler.PAN_MOTOR_TIMEBASE_ALIGNMENT
    DATA_FILE_PATH = DATA_DIR_PATH / DATA_FILENAME

    TEST_OBJ = {
        'string_a': 'a string',
        'list_a': [1, 2, 3, 4],
        'int': 1
    }

    def setUp(self):
        self.cdf = CalibrationDataFiler(self.__class__.TOP_LEVEL_PATH)
        self.remove_data_dir_and_top_level_dir()

    def test_ensure_data_dir(self):
        self.assertFalse(os.path.isdir(self.__class__.DATA_DIR_PATH))
        self.assertFalse(os.path.isdir(self.__class__.TOP_LEVEL_PATH))
        self.cdf._ensure_data_dir(self.__class__.DATA_DIR_NAME)
        self.assertTrue(os.path.isdir(self.__class__.DATA_DIR_PATH))
        self.assertTrue(os.path.isdir(self.__class__.TOP_LEVEL_PATH))

    def test_save_as_yml(self):
        self.assertFalse(os.path.isfile(self.__class__.DATA_FILE_PATH))
        self.save_as_yml()
        self.assertTrue(os.path.isfile(self.__class__.DATA_FILE_PATH))

    def test_load(self):
        self.save_as_yml()
        obj = self.load()
        self.assertDictEqual(obj, self.__class__.TEST_OBJ)

    def test_load_with_no_file_returns_none(self):
        self.assertIsNone(self.load())

    def remove_data_dir_and_top_level_dir(self):
        if self.DATA_DIR_PATH.is_dir():
            for file_path in self.__class__.DATA_DIR_PATH.iterdir():
                if os.path.isfile(file_path):
                    os.remove(file_path)

        if os.path.isdir(self.__class__.DATA_DIR_PATH):
            os.rmdir(self.__class__.DATA_DIR_PATH)
        if os.path.isdir(self.__class__.TOP_LEVEL_PATH):
            os.rmdir(self.__class__.TOP_LEVEL_PATH)

    def save_as_yml(self):
        self.cdf.save_as_yml(self.__class__.TEST_OBJ,
                             self.__class__.DATA_DIR_NAME,
                             self.__class__.DATA_FILENAME,
                            )

    def load(self):
        return self.cdf.load(self.__class__.DATA_DIR_NAME,
                             self.__class__.DATA_FILENAME,
                            )

if __name__ == '__main__':
    unittest.main()
