import pyvisa
import time
import timeit
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import Instr_lib as instrlib
import zhinst.core

rm = pyvisa.ResourceManager()
print(rm.list_resources())

# Initialize instrument object using pyvisa
addr5 = rm.open_resource('GPIB0::5::INSTR')
addr9 = rm.open_resource('GPIB0::9::INSTR')
FunctionGenerator = rm.open_resource('GPIB0::19::INSTR')
SourceMeter = rm.open_resource('GPIB0::20::INSTR')

# Measurement config
FunctionGenerator.write("*CLS")
SourceMeter.write('*RST')
SourceMeter.write(":ROUT:TERM REAR")
SourceMeter.write(":SOUR:FUNC CURR")
SourceMeter.write(":SOUR:CURR:MODE FIX")
SourceMeter.write(":SOUR:CURR:RANGe 0.01")

# MFLI by Zurich Instrument config
device_id = "dev7173" # Device serial number available on its rear panel.
interface = "1GbE" # For Ethernet connection or when MFLI/MFIA is connected to a remote Data Server.
#interface = "PCIe" # For MFLI/MFIA devices in case the Data Server runs on the device.
server_host = "localhost"
server_port = 8004
api_level = 6 # 

daq = zhinst.core.ziDAQServer(server_host, server_port, api_level)
daq.connectDevice(device_id, interface)
daq.set(f"/{device_id}/demods/0/enable", 1)
demod_path = f"/{device_id}/demods/0/sample"
signal_paths = []

total_duration = 3 # Time in seconds for the aquisition.
module_sampling_rate = 30000  # Number of points/second.
burst_duration = 0.2  # Time in seconds for each data burst/segment.
num_cols = int(np.ceil(module_sampling_rate * burst_duration))
num_bursts = int(np.ceil(total_duration / burst_duration))

daq_module = daq.dataAcquisitionModule()
daq_module.set("device", device_id)

daq_module.set("type", "continuous")
daq_module.set("grid/mode", "linear")
daq_module.set("count", num_bursts)
daq_module.set("duration", burst_duration)
daq_module.set("grid/cols", num_cols)

filename = "Sensitivity measurement"
daq_module.set("save/fileformat", "csv")
daq_module.set("save/filename", filename)
daq_module.set("save/saveonread", True)

# Lock-in demodulated signal data acquisition
signal_paths.append(demod_path + ".r")  # The demodulator R output.
signal_paths.append(demod_path + ".frequency")  # The demodulator frequency output.

# MTJ sensor current
SourceMeter.write(":SOUR:CURR 0.001")

SourceMeter.write(":OUTP ON")
FunctionGenerator.write("OUTP:LOAD 50")

# Function generator parameters
AC_on = 1
offset = 0
frequency = 100
Vpp = 1

if AC_on != 1:
    FunctionGenerator.write("APPL:DC DEF, DEF, 0V")
elif AC_on == 1:
    FunctionGenerator.write("APPL:SIN 500 HZ, 1 VPP")

# Lock-In Data Acquisition
data = {}
for signal_path in signal_paths:
    print("Subscribing to ", signal_path)
    daq_module.subscribe(signal_path)
    data[signal_path] = []

do_plot = True
clockbase = float(daq.getInt(f"/{device_id}/clockbase"))
if do_plot:
    timestamp0 = None
    max_value = None
    min_value = None
    fig, axis = plt.subplots()
    axis.set_xlabel("Time (s)")
    axis.set_ylabel("Subscribed signals")
    axis.set_xlim([0, total_duration])
    lines = [axis.plot([], [], label=path)[0] for path in signal_paths]
    axis.legend()
    axis.set_title("Continuous Data Acquisition")
    plt.ion()
    

def process_data(raw_data):
    global timestamp0, lines, max_value, min_value
    for i, signal_path in enumerate(signal_paths):
        # Loop over all the bursts for the subscribed signal. More than
        # one burst may be returned at a time, in particular if we call
        # read() less frequently than the burst_duration.
        for signal_burst in raw_data.get(signal_path.lower(), []):
            # Convert from device ticks to time in seconds.
            value = signal_burst["value"][0, :]
            data[signal_path].append(value)
            if do_plot:
                max_value = max(max_value, max(value)) if max_value else max(value)
                min_value = min(min_value, min(value)) if min_value else min(value)
                axis.set_ylim(min_value, max_value)
                timestamp0 = (
                    timestamp0 if timestamp0 else signal_burst["timestamp"][0, 0]
                )
                t = (signal_burst["timestamp"][0, :] - timestamp0) / clockbase
                lines[i].set_data(
                    np.concatenate((lines[i].get_xdata(), t), axis=0),
                    np.concatenate((lines[i].get_ydata(), value), axis=0),
                )
    if do_plot:
        fig.canvas.draw()

# Start recording data.
daq_module.execute()
# Record data in a loop with timeout.
timeout = 1.5 * total_duration
start = time.time()

while not daq_module.finished():
    t0_loop = time.time()
    if time.time() - start > timeout:
        raise Exception(
            f"Timeout after {timeout} s - recording not complete."
            "Are the streaming nodes enabled?"
            "Has a valid signal_path been specified?"
        )
    raw_data = daq_module.read(True)
    process_data(raw_data)
    time.sleep(max(0, burst_duration - (time.time() - t0_loop)))

raw_data = daq_module.read(True)
process_data(raw_data)

r = raw_data['/dev7173/demods/0/sample.r']

np.savetxt('rdata.txt', r)







k,m 
print(FunctionGenerator.query("SYST:ERR?"))
print(SourceMeter.query("SYST:ERR?"))










'''
#daq = zhinst.core.ziDAQServer('127.0.0.1', 8004, 6)
# Starting module scopeModule on 2023/10/23 16:16:16
scope = daq.scopeModule()
scope.set('lastreplace', 1)
scope.subscribe('/dev7173/scopes/0/wave')
scope.set('averager/weight', 1)
scope.set('averager/restart', 0)
scope.set('averager/weight', 1)
scope.set('averager/restart', 0)
scope.set('fft/power', 0)
scope.unsubscribe('*')
scope.set('mode', 1)
scope.set('fft/spectraldensity', 0)
scope.set('fft/window', 1)
scope.set('save/directory', '/data/LabOne/WebServer')
scope.subscribe('/dev7173/demods/0/sample')
scope.execute()
# To read the acquired data from the module, use a
# while loop like the one below. This will allow the
# data to be plotted while the measurement is ongoing.
# Note that any device nodes that enable the streaming
# of data to be acquired, must be set before the while loop.
# result = 0
# while not scope.finished():
#     time.sleep(1)
#     result = scope.read()
#     print(f"Progress {float(scope.progress()) * 100:.2f} %\r")
daq.setInt('/dev7173/scopes/0/trigforce', 1)
daq.setInt('/dev7173/sigins/0/ac', 1)
daq.setInt('/dev7173/sigins/0/autorange', 1)
daq.setInt('/dev7173/scopes/0/trigforce', 1)

time.sleep(0.1)
result = scope.read()
print(f"Progress {float(scope.progress()) * 100:.2f} %\r")



for i in result:
    print(i)
    
print(daq.poll(0.200, 10, 0, True))
'''