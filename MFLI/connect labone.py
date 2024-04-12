import pyvisa
import time
import timeit
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import zhinst.core
import pickle
import csv

rm = pyvisa.ResourceManager()
print(rm.list_resources())

# Initialize instrument object using pyvisa
addr19 = rm.open_resource('GPIB0::19::INSTR')

addr19.write('*CLS')
addr19.write('*RST')

device_id = "dev7173" # Device serial number available on its rear panel.
interface = "1GbE" # For Ethernet connection or when MFLI/MFIA is connected to a remote Data Server.

server_host = "localhost"
server_port = 8004
api_level = 1 # Maximum API level supported for all instruments except HF2LI.

# Create an API session to the Data Server.
daq = zhinst.core.ziDAQServer(server_host, server_port, api_level)
# Establish a connection between Data Server and Device.
daq.connectDevice(device_id, interface)

lowpass_order = 3


demod_path = f"/{device_id}/demods/0/sample"

total_duration = 1 # Time in seconds for the aquisition.
module_sampling_rate = 10000  # Number of points/second.
burst_duration = 0.2  # Time in seconds for each data burst/segment.
num_cols = int(np.ceil(module_sampling_rate * burst_duration))
num_bursts = int(np.ceil(total_duration / burst_duration))

daq_module = daq.dataAcquisitionModule()

daq_module.set("device", device_id)


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

def Lock_In_measure(volt, freq):
    addr19.write("OUTP:LOAD 50")

    offset = 0
    AC_on = 1
    freq = freq
    Vpk = volt
    if AC_on != 1:
        addr19.write("APPL:DC DEF, DEF, "+ str(offset)+ "V")
    elif AC_on == 1:
        addr19.write("APPL:SIN "+str(freq)+" HZ, "+str(Vpk)+" VPP, "+ str(offset)+ "V")
     

    # ==================================== Lock-in Amplifier ===========================================

    daq.set(f"/{device_id}/extrefs/0/enable", 1)
    daq.set(f"/{device_id}/demods/1/adcselect", 8)
    daq.set(f"/{device_id}/sigins/0/ac", 1)
    daq.set(f"/{device_id}/demods/0/order", lowpass_order)
    daq.set(f"/{device_id}/demods/0/order", lowpass_order)

    daq.set(f"/{device_id}/sigins/0/autorange", 1)
    time.sleep(0.1)
    daq.set(f"/{device_id}/sigins/0/autorange", 1)
    daq.set(f"/{device_id}/demods/0/sinc", 1)

    daq.set(f"/{device_id}/demods/0/enable", 1)

    # Specify continuous acquisition. (continuous = 0)
    daq_module.set('triggernode', '/dev7173/demods/0/sample.R')
    daq_module.set("type", "continuous")
    daq_module.set("grid/mode", 4)
    daq_module.set("count", num_bursts)
    daq_module.set("duration", burst_duration)
    daq_module.set("grid/cols", num_cols)     
    daq_module.set('forcetrigger', 1)      
    
    MFLI_outputs = ['r', 'frequency']
    signal_paths = []
    for i in MFLI_outputs:
        signal_paths.append(demod_path + "." + i)  # The demodulator output.

    data = {}
    for signal_path in signal_paths:
        print("Subscribing to ", signal_path)
        daq_module.subscribe(signal_path)
        time.sleep(0.2)
        data[signal_path] = []

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
        

    # Start recording data.
    daq_module.execute()
    # Record data in a loop with timeout.
    timeout = 25 * total_duration
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
        time.sleep(max(0, burst_duration - (time.time() - t0_loop))+0.3)
    # There may be new data between the last read() and calling finished().
    raw_data = daq_module.read(True)
    process_data(raw_data)
    print(raw_data)
    #r = raw_data['/dev7173/demods/0/sample.r'][0]
    #print('This is r:', r)


    def getOutputs(MFLI_outputs, signal_paths, raw_data):
        data = {}
        keys = ['timestamp', 'value']
        def extracttv(data, keys):
            data = {
                    keys[0]: data[keys[0]][0] - data[keys[0]][0][0],
                    keys[1]: data[keys[1]][0]
                    }
            return data
        for i, sig in enumerate(signal_paths):
            data[MFLI_outputs[i]] = extracttv(raw_data[sig][0], keys)
            
        #print(data)
        return data
    data = getOutputs(MFLI_outputs, signal_paths, raw_data)

    with open('MTJ_signal.pkl', 'wb') as fp:
        pickle.dump(data, fp)
        print('dictionary saved successfully to file')

    # ==================================== Sensitivity calculation =====================================

    r_ave = np.average(data['r']['value'])
    r_std = np.std(data['r']['value'])
    freq_ave = np.average(data['frequency']['value'])
    freq_std = np.std(data['frequency']['value'])

    print(addr19.query("SYST:ERR?"))
    
    return r_ave, freq_ave

# Function ends

result = Lock_In_measure(1, 100)

print(result)
