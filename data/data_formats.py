# pylint: disable=C0103
from pathlib import Path
import numpy as np

NPZ_DIR = Path('.') / 'data'  # Change this to match your test directory structure
BASE_NPZ_PATH = NPZ_DIR / 'base.npz'

dummy_data = np.arange(15)

np.savez(BASE_NPZ_PATH,
         motor_time=dummy_data,
         pan_motor_read=dummy_data,
         tilt_motor_read=dummy_data,
         base_lat=dummy_data,
         base_long=dummy_data,
         base_alt=dummy_data,
         base_tilt_at_current_pan_angle=dummy_data,
         base_roll_at_current_pan_angle=dummy_data,
         cam_pitch=dummy_data,
        )

base_npz = np.load(BASE_NPZ_PATH)

fields = base_npz.files
print(fields)
# ['motor_time',
#  'pan_motor_read',
#  'tilt_motor_read',
#  'base_lat',
#  'base_long',
#  'base_alt',
#  'base_tilt_at_current_pan_angle',
#  'base_roll_at_current_pan_angle',
#  'cam_pitch']

for field in fields:
    data = base_npz[field]
    print(field, data)

# motor_time [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14]
# pan_motor_read [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14]
# tilt_motor_read [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14]
# base_lat [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14]
# base_long [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14]
# base_alt [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14]
# base_tilt_at_current_pan_angle [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14]
# base_roll_at_current_pan_angle [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14]
# cam_pitch [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14]



motor_time
pan_motor_read
tilt_motor_read
base_lat
base_long
base_alt
base_tilt_at_current_pan_angle
base_roll_at_current_pan_angle
cam_pitch