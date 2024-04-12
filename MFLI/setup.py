import pyvisa
import time
import timeit
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import zhinst.core
import pickle
import csv




device_id = "dev7173" # Device serial number available on its rear panel.
interface = "1GbE" # For Ethernet connection or when MFLI/MFIA is connected to a remote Data Server.

server_host = "localhost"
server_port = 8004
api_level = 6 # Maximum API level supported for all instruments except HF2LI.

# Create an API session to the Data Server.
daq = zhinst.core.ziDAQServer(server_host, server_port, api_level)
# Establish a connection between Data Server and Device.
daq.connectDevice(device_id, interface)

lowpass_order = 3

daq.set(f"/{device_id}/sigins/0/ac", 1)
daq.set(f"/{device_id}/demods/0/order", lowpass_order)

daq.set(f"/{device_id}/sigins/0/autorange", 0)
daq.set(f"/{device_id}/demods/0/sinc", 1)

daq.set(f"/{device_id}/demods/0/enable", 1)
demod_path = f"/{device_id}/demods/0/sample"

total_duration = 3 # Time in seconds for the aquisition.
module_sampling_rate = 90000  # Number of points/second.
burst_duration = 0.2  # Time in seconds for each data burst/segment.
num_cols = int(np.ceil(module_sampling_rate * burst_duration))
num_bursts = int(np.ceil(total_duration / burst_duration))

daq_module = daq.dataAcquisitionModule()

daq_module.set("device", device_id)

# Specify continuous acquisition. (continuous = 0)
daq_module.set("type", "continuous")
daq_module.set("grid/mode", "linear")
daq_module.set("count", num_bursts)
daq_module.set("duration", burst_duration)
daq_module.set("grid/cols", num_cols)

# Lock-in configuration
in_channel = 0
lowpass_order = 3
exp_setting = [
        # The output signal.
        ["/%s/sigins/%d/ac" % (device_id, in_channel), 1],
        ["/%s/demods/%d/order" % (device_id, in_channel), lowpass_order],
        ["/%s/sigins/%d/autorange" % (device_id, in_channel), 1],
        ["/%s/demods/%d/sinc" % (device_id, in_channel), 1],
    ]
#daq.setInt(exp_setting)