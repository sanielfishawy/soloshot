from pathlib import Path
import numpy as np

DATA_DIR = Path('.') / 'data'

MOTOR_DATA_FILENAME = 'motor.npz'

MOTOR_TIME = 'motor_time'
PAN_MOTOR_READ = 'pan_motor_read'
TILT_MOTOR_READ = 'tilt_motor_read'
MOTOR_LEGEND = np.array([
    [MOTOR_TIME],
    [PAN_MOTOR_READ],
    [TILT_MOTOR_READ]
])

motor_data = np.arange(15).reshape(3,5)

MOTOR_DATA_PATH = DATA_DIR / MOTOR_DATA_FILENAME
np.savez(MOTOR_DATA_PATH, motor_legend=MOTOR_LEGEND, motor_data=motor_data)

motor_npz = np.load(MOTOR_DATA_PATH)

print(motor_npz.files)

motor_legend = motor_npz['motor_legend']
print(motor_legend)

motor_data = motor_npz['motor_data']
print(motor_data)


