import pyvisa
import time
import timeit
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import zhinst.core
import pickle
import csv

X_magnet_GPA = 132.3129
Y_magnet_GPA = 129.76684
X_HHC_GPA = 31.72649
Y_HHC_GPA = 31.82234
shunt5 = 5.120274518
shunt1k = 982.7692212
shunt10k = 9887.211007
shunt100k = 98352.2549
shunt2M = 2022572

rm = pyvisa.ResourceManager()
print(rm.list_resources())

# Initialize instrument object using pyvisa
#addr5 = rm.open_resource('GPIB0::5::INSTR')
#addr9 = rm.open_resource('GPIB0::9::INSTR')
addr10 = rm.open_resource('GPIB0::10::INSTR')
addr19 = rm.open_resource('GPIB0::19::INSTR')
addr20 = rm.open_resource('GPIB0::20::INSTR')
addr26 = rm.open_resource('GPIB0::26::INSTR')

addr19.write('*CLS')
addr19.write('*RST')
addr20.write('*RST')
addr20.write("SOUR:FUNC CURR")
addr20.write("SOUR:CURR:MODE FIX")
addr20.write("SOUR:CURR:RANGe 0.01")

  
addr20.write("NPLC .03")  
addr20.write("SENS:VOLT:PROT 10")
addr20.write("SENS:CURR:PROT 0.003")
addr20.write("SENS:FUNC \"VOLT\"")
addr20.write("SENS:VOLT:RANG 10")
addr20.write("FORM:ELEM VOLT")




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

def sensitivity_measure(volt, freq, switch_position, MTJ_curr=0.001):
    # volt(float): voltage amplitude of the signal from function generator
    # freq: frequency(float) of the signal from function generator
    # switch_position(string): name of the shunt resistor resistance in the switch:
    #                          'Pos 1': shunt5
    #                          'Pos 2': shunt1k
    #                          'Pos 3': shunt10k
    #                          'Pos 4': shunt100k
    #                          'Pos 5': shunt2M
    

    # MTJ sensor DC current control
    #print(MTJ_curr)
    addr20.write("SOUR:CURR ", str(MTJ_curr))

    addr20.write("OUTP ON")
    addr19.write("OUTP:LOAD 50")

    offset = 0
    AC_on = 1
    freq = freq
    Vpk = volt
    if AC_on != 1:
        addr19.write("APPL:DC DEF, DEF, "+ str(offset)+ "V")
    elif AC_on == 1:
        addr19.write("APPL:SIN "+str(freq)+" HZ, "+str(Vpk)+" VPP, "+ str(offset)+ "V")
     

    print(addr10.query("SYST:ERR?"))

    # ==================================== Lock-in Amplifier ===========================================

    daq.set(f"/{device_id}/extrefs/0/enable", 1)
    daq.set(f"/{device_id}/demods/1/adcselect", 8)
    daq.set(f"/{device_id}/sigins/0/ac", 1)
    daq.set(f"/{device_id}/demods/0/order", lowpass_order)

    daq.set(f"/{device_id}/sigins/0/autorange", 1)
    time.sleep(0.2)
    daq.set(f"/{device_id}/sigins/0/autorange", 1)
    daq.set(f"/{device_id}/demods/0/sinc", 1)

    daq.set(f"/{device_id}/demods/0/enable", 1)

    # Specify continuous acquisition. (continuous = 0)
    daq_module.set('triggernode', '/dev7173/demods/0/sample.R')
    daq_module.set("type", "continuous")
    daq_module.set("grid/mode", "linear")
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

    shuntVolt = float(addr10.query("MEAS:VOLT:AC?"))
    shunt = {
             'Pos 1': shunt5,
             'Pos 2': shunt1k,
             'Pos 3': shunt10k,
             'Pos 4': shunt100k,
             'Pos 5': shunt2M,
            }
    HHC_Ipk = shuntVolt/shunt[switch_position]*np.sqrt(2)
    GPA = X_HHC_GPA
    HHC_Hpk = HHC_Ipk * GPA
    dc_component = float(addr26.query('F0')[4:])
    #print('Shunt voltage: ', shuntVolt)
    #print('H field calculated: ', HHC_Hpk)
    #print('DC component: ', dc_component)
    r_ave = np.average(data['r']['value'])
    r_std = np.std(data['r']['value'])
    freq_ave = np.average(data['frequency']['value'])
    freq_std = np.std(data['frequency']['value'])
    MTJ_Vpk = r_ave*np.sqrt(2)
    percent_delta = MTJ_Vpk/dc_component
    Sensitivity = percent_delta/HHC_Hpk*100
    #print("MTJ signal amplitude: ", str(MTJ_Vpk), "V")
    print("\n Sensitivity: ", str(Sensitivity), "%/G \n")
    
    measurement = {
                   'FG Signal amplitude(V)': Vpk,
                   'Signal frequency(Hz)': freq_ave,
                   'Signal freq_std(Hz)': freq_std,
                   'MTJ operating current(A)': MTJ_curr,
                   'Voltage of shunt R(V)': shuntVolt,
                   'Shunt resistance(Ohm)': shunt[switch_position],
                   'R average': r_ave,
                   'R std': r_std,
                   'DC component': dc_component,
                   'HHC field amplitude(G)': HHC_Hpk,
                   'MTJ signal amplitude(V)': MTJ_Vpk,
                   'Percent change': percent_delta,
                   'Sensitivity(%/G)': Sensitivity
                  }

    # Power off
    #addr20.write(":OUTP OFF")
    #addr19.write("APPL:DC DEF, DEF, 0V")
    print( '\n',
          'Raw data: ', '\n', 
          'shuntVolt: ', shuntVolt, '\n', 
          'shunt: ', shunt[switch_position], '\n', 
          'HHC_Ipp: ', HHC_Ipk,  '\n', 
          'dc_component: ', dc_component,  '\n', 
          'r_ave: ', r_ave,
           '\n')
          

    print(addr10.query("SYST:ERR?"))
    print(addr19.query("SYST:ERR?"))
    print(addr20.query("SYST:ERR?"))
    
    return measurement

# Function ends

start = timeit.default_timer()
'''
volt_FG = 1
freq_FG = 95
shunt_input = 'Pos 1'
result = [sensitivity_measure(volt_FG, freq_FG, shunt_input)]
print(result)
with open('Sensitivity.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, result[0].keys())
    writer.writeheader()
    writer.writerows(result)

'''
sensitivities = []
#volts = [0.75]
volts = np.arange(.72, 0.05, -.01)
#f = 1503
shunt_select = 3 # !!! Remember to change the position of the switch
fs = np.multiply([16], 95)-17

for f in fs:
    for v in volts:
        s = sensitivity_measure(v, f, 'Pos ' + str(shunt_select))
        stop = timeit.default_timer()
        s['Real time(s)'] = stop - start
        sensitivities.append(s)
        print('Time: ', stop - start, 's')
        with open('Sensitivity.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, sensitivities[0].keys())
            writer.writeheader()
            writer.writerows(sensitivities)
        print(sensitivities)
    
#print(sensitivities)
