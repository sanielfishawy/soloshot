import os
from pathlib import Path
import yaml

class CalibrationDataFiler:
    ''' Handles saving and loading calibration data'''

    # Calibration data filenames
    PAN_MOTOR_TIMEBASE_ALIGNMENT = 'pan_motor_timebase_alignment.yml'

    def __init__(self, top_level_dir: Path):
        self._top_level_dir = top_level_dir

    def save_as_yml(self, obj, data_dir_name: str, calibration_file: str):
        '''
        :param Path data_dir_name: by convention this should be the same as session_dir \
                              containg the input data
        '''
        self._ensure_data_dir(data_dir_name)
        yaml_file = self._get_file_path(data_dir_name, calibration_file)
        with open(yaml_file, 'w') as yaml_file:
            yaml.dump(obj, yaml_file, default_flow_style=False)

    def load(self, data_dir_name: str, calibration_filename: str):
        filepath = self._get_file_path(data_dir_name, calibration_filename)
        if not filepath.is_file():
            return None
        with open(self._get_file_path(data_dir_name, calibration_filename), 'r') as stream:
            return yaml.load(stream)

    def _get_file_path(self, data_dir_name: str, filename: str) -> Path:
        return (self._get_data_dir_path(data_dir_name) / filename).resolve()

    def _ensure_data_dir(self, data_dir_name: str):
        '''
        :param Path data_dir: by convention this should be the same as session_dir \
                              containg the input data
        '''
        path = Path('/')
        for part in self._get_data_dir_path(data_dir_name).resolve().parts:
            path = path / part
            if not os.path.isdir(path):
                os.mkdir(path)

    def _get_data_dir_path(self, data_dir_name):
        return self._top_level_dir / data_dir_name