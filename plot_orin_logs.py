import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from analyze import *

# Get the path to the pi_logs folder
logs_folder = '/home/robinferede/Git/analyze_flight_data/orin_logs'

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
# rename keys such that there are no ' ' in the keys
data = data.rename(columns=lambda x: x.strip())
# convert to dict of numpy arrays
data = {key: data[key].to_numpy() for key in data.keys()}
# down sample
data = {key: data[key][::10] for key in data.keys()}

# trim data
indices_of_interest = (data['ext_time_us'] > 0) & (data['vio_time_us'] > 0)
data = {key: data[key][indices_of_interest] for key in data.keys()}

# convert vio to optitrack frame
# ----------------------------------------------
# vio axis = (FLU)(rotated by 180) = (BRU)
# ext axis = (NED) = (FLD)
data['vio_x'] = -data['vio_x']
data['vio_z'] = -data['vio_z']
data['vio_qx'] = -data['vio_qx']
data['vio_qz'] = -data['vio_qz']

# compute euler angles
data['ext_phi'] = np.arctan2(2*(data['ext_qw']*data['ext_qx']+data['ext_qy']*data['ext_qz']), 1-2*(data['ext_qx']**2+data['ext_qy']**2))
data['ext_theta'] = np.arcsin(2*(data['ext_qw']*data['ext_qy']-data['ext_qz']*data['ext_qx']))
data['ext_psi'] = np.arctan2(2*(data['ext_qw']*data['ext_qz']+data['ext_qx']*data['ext_qy']), 1-2*(data['ext_qy']**2+data['ext_qz']**2))

data['vio_phi'] = np.arctan2(2*(data['vio_qw']*data['vio_qx']+data['vio_qy']*data['vio_qz']), 1-2*(data['vio_qx']**2+data['vio_qy']**2))
data['vio_theta'] = np.arcsin(2*(data['vio_qw']*data['vio_qy']-data['vio_qz']*data['vio_qx']))
data['vio_psi'] = np.arctan2(2*(data['vio_qw']*data['vio_qz']+data['vio_qx']*data['vio_qy']), 1-2*(data['vio_qy']**2+data['vio_qz']**2))

print((data['ext_time_us']-data['ext_time_us'][0])*1e-6)

# get trajectory for optitrack
traj_opti = {
    't': (data['ext_time_us']-data['ext_time_us'][0])*1e-6,
    'x': data['ext_x'],
    'y': data['ext_y'],
    'z': data['ext_z'],
    'phi': data['ext_phi'],
    'theta': data['ext_theta'],
    'psi': data['ext_psi'],
    'u1': np.zeros_like(data['ext_time_us']),
    'u2': np.zeros_like(data['ext_time_us']),
    'u3': np.zeros_like(data['ext_time_us']),
    'u4': np.zeros_like(data['ext_time_us']),
}

traj_vio = {
    't': (data['vio_time_us']-data['vio_time_us'][0])*1e-6,
    'x': data['vio_x'],
    'y': data['vio_y'],
    'z': data['vio_z'],
    'phi': data['vio_phi'],
    'theta': data['vio_theta'],
    'psi': data['vio_psi'],
    'u1': np.zeros_like(data['vio_time_us']),
    'u2': np.zeros_like(data['vio_time_us']),
    'u3': np.zeros_like(data['vio_time_us']),
    'u4': np.zeros_like(data['vio_time_us']),
}

animate_data_multiple(traj_opti, traj_vio)

# comparison plot of ext: x,y,z and vio: x,y,z
fig, axs = plt.subplots(3, 1, figsize=(15, 10), sharex=True)
axs[0].plot(traj_opti['t'], traj_opti['x'], label='optitrack')
axs[0].plot(traj_vio['t'], traj_vio['x'], label='vio')
axs[0].set_title('x')
axs[0].grid()
axs[0].legend()
axs[1].plot(traj_opti['t'], traj_opti['y'], label='optitrack')
axs[1].plot(traj_vio['t'], traj_vio['y'], label='vio')
axs[1].set_title('y')
axs[1].grid()
axs[1].legend()
axs[2].plot(traj_opti['t'], traj_opti['z'], label='optitrack')
axs[2].plot(traj_vio['t'], traj_vio['z'], label='vio')
axs[2].set_title('z')
axs[2].grid()
axs[2].legend()
plt.show()

