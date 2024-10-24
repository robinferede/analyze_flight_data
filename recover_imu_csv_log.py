from analyze import *
import os

path = 'flight_data/Okt12_Orin_drone_TT2.csv'
data = load_flight_data(path)

import pandas as pd
orin_csv_mocap_log = '/home/robinferede/Git/dronerace/logs/73/optitrack_logs/optitrack-1970-1-1-1-3-22.csv'

df = pd.read_csv(orin_csv_mocap_log, skipinitialspace=True)

print(df.keys())

orin_time = np.array(df['orin_time'])
orin_opti_x = np.array(df['optitrack_x'])
orin_opti_y = np.array(df['optitrack_y'])
orin_opti_z = np.array(df['optitrack_z'])

bbl_time = data['t']
bbl_opti_x = data['x_opti']
bbl_opti_y = data['y_opti']
bbl_opti_z = data['z_opti']

shift = 213.88
plt.plot(orin_time, orin_opti_x, label='x')
plt.plot(bbl_time+shift, bbl_opti_x, label='x')
# plt.xlim([225,228])
plt.show()

plt.plot(orin_time, orin_opti_y, label='y')
plt.plot(bbl_time+shift, bbl_opti_y, label='y')
# plt.xlim([225,228])
plt.show()

plt.plot(orin_time, orin_opti_z, label='z')
plt.plot(bbl_time+shift, bbl_opti_z, label='z')
# plt.xlim([225,228])
plt.show()

# we have to find the blackbox log that matches the following csv file:
orin_csv_imu_log = '/home/robinferede/Git/dronerace/logs/73/uart_logs/imu-1970-1-1-1-3-22.csv'

# load csv file into a pandas dataframe
import pandas as pd
from scipy import signal
# ignore spaces in the csv file
df = pd.read_csv(orin_csv_imu_log, skipinitialspace=True)

# print keys of the dataframe
print(df.keys())

# orin logs
imu_t = np.array(df['imu_time'])
print('freq imu', 1/np.mean(np.diff(imu_t)))
imu_x = np.array(df['imu_x'])
imu_y = np.array(df['imu_y'])
imu_z = np.array(df['imu_z'])
imu_p = np.array(df['imu_roll'])
imu_q = np.array(df['imu_pitch'])
imu_r = np.array(df['imu_yaw'])

# bbl logs
bbl_t = data['t']
print('freq bbl', 1/np.mean(np.diff(bbl_t)))
bbl_x = data['ax_unfiltered']
bbl_y = data['ay_unfiltered']
bbl_z = data['az_unfiltered']
bbl_p = data['p']
bbl_q = data['q']
bbl_r = data['r']

plt.plot(imu_t, imu_x, label='imu_x')
plt.plot(bbl_t+shift, bbl_x, label='bbl_x')
plt.xlim([225,226])
plt.legend()
plt.show()

plt.plot(imu_t, imu_p, label='imu_p')
plt.plot(bbl_t+shift, bbl_p, label='bbl_p')
plt.xlim([225,226])
plt.legend()
plt.show()

