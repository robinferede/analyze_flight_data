import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Get the path to the pi_logs folder
logs_folder = '/home/robinferede/Git/analyze_flight_data/pi_logs'

# Get a list of all log files in the folder
log_files = os.listdir(logs_folder)

# each file is named imu-YYYY-DD-MM-TT-TT-TT.csv
# sort the files by date
log_files.sort()

# let the user select the file
print('Select a file to plot:')
for i, file in enumerate(log_files):
    print(f'{i}: {file}')
file_index = int(input('Enter the index of the file to plot: '))
log_file = log_files[file_index]

# Load the data from the log file
data = pd.read_csv(os.path.join(logs_folder, log_file))
# remove last row
data = data.iloc[:-1]

# extra
data['imu_time_ms'] -= data['imu_time_ms'][0]
data['imu_time_s'] = data['imu_time_ms'] / 1000
# imu frequency
imu_dt = np.mean(np.diff(data['imu_time_ms']))*1e-3
imu_freq = 1/imu_dt
# check if nan
if np.isnan(imu_freq):
    imu_freq = 0

# Plot the data (for now just the imu)
# time_ms,imu_time_ms, imu_p, imu_q, imu_r, imu_ax, imu_ay, imu_az,ext_x, ext_y, ext_z, ext_vx, ext_vy, ext_vz, ext_qw, ext_qx, ext_qy, ext_qz,
# subplots
fig, axs = plt.subplots(2, 3, figsize=(15, 10), sharex=True, sharey='row')
axs[0, 0].plot(data['imu_time_s'], data['imu_ax'], label='ax')
axs[0, 0].set_ylim(-160, 160)
axs[0, 1].plot(data['imu_time_s'], data['imu_ay'], label='ay')
axs[0, 1].set_ylim(-160, 160)
axs[0, 2].plot(data['imu_time_s'], data['imu_az'], label='az')
axs[0, 2].set_ylim(-160, 160)
axs[1, 0].plot(data['imu_time_s'], data['imu_p'], label='p')
axs[1, 1].plot(data['imu_time_s'], data['imu_q'], label='q')
axs[1, 2].plot(data['imu_time_s'], data['imu_r'], label='r')
axs[0, 0].set_title('ax')
axs[0, 1].set_title('ay')
axs[0, 2].set_title('az')
axs[1, 0].set_title('p')
axs[1, 1].set_title('q')
axs[1, 2].set_title('r')
for ax in axs.flat:
    ax.grid()
title = f'IMU data from: {log_file} \n logged at {int(imu_freq)} Hz'
fig.suptitle(title)
plt.show()


