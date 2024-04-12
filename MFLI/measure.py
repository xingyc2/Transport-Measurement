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
addr20.write("SENS:CURR:PROT 0.004") 
addr20.write("SENS:FUNC \"VOLT\"")
addr20.write("SENS:VOLT:RANG 10")
addr20.write("FORM:ELEM VOLT")

device_id = "dev7173" # Device serial number available on its rear panel.
interface = "1GbE" # For Ethernet connection or when MFLI/MFIA is connected to a remote Data Server.

lowpass_order = 3
server_host = "localhost"
server_port = 8004
api_level = 6 # Maximum API level supported for all instruments except HF2LI.
demod_path = f"/{device_id}/demods/0/sample"

def sensitivity_measure(volt, freq, switch_position, MTJ_curr=0.003):
    # volt(float): voltage amplitude of the signal from function generator
    # freq: frequency(float) of the signal from function generator
    # switch_position(string): name of the shunt resistor resistance in the switch:
    #                          'Pos 1': shunt5
    #                          'Pos 2': shunt1k
    #                          'Pos 3': shunt10k
    #                          'Pos 4': shunt100k
    #                          'Pos 5': shunt2M
    

    # MTJ sensor DC current control
    print(MTJ_curr)
    addr20.write("SOUR:CURR ", str(MTJ_curr))

    addr20.write("OUTP ON")
    #addr19.write("OUTP:LOAD 50")

    offset = 0
    AC_on = 1
    freq = freq
    Vpk = volt/X_HHC_GPA
    if AC_on != 1:
        addr19.write("APPL:DC DEF, DEF, "+ str(offset)+ "V")
    elif AC_on == 1:
        addr19.write("APPL:SIN "+str(freq)+" HZ, "+str(Vpk)+" VPP, "+ str(offset)+ "V")
     

    print(addr10.query("SYST:ERR?"))

    # ==================================== Lock-in Amplifier ===========================================

    MFLI_outputs = ['r', 'frequency']
    
    signal_paths = []
    for i in MFLI_outputs:
        signal_paths.append(demod_path + "." + i)  # The demodulator output.

    data = {}
    for signal_path in signal_paths:
        print("Subscribing to ", signal_path)
        daq_module.subscribe(signal_path)
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
    # There may be new data between the last read() and calling finished().
    raw_data = daq_module.read(True)
    process_data(raw_data)

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
            
        print(data)
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
    HHC_Ipp = shuntVolt/shunt[switch_position]*np.sqrt(2)*2
    GPA = X_HHC_GPA
    HHC_Hpp = HHC_Ipp * GPA
    dc_component = float(addr26.query('F0')[4:])
    print('Shunt voltage: ', shuntVolt)
    print('H field calculated: ', HHC_Hpp)
    print('DC component: ', dc_component)
    r_ave = np.average(data['r']['value'])
    MTJ_Vpp = r_ave*np.sqrt(2)*2
    percent_delta = MTJ_Vpp/dc_component
    Sensitivity = percent_delta/HHC_Hpp*100
    print("Sensitivity: ", str(Sensitivity), "%/G")
    
    measurement = {
                   'Signal amplitude(V)': Vpk,
                   'Signal frequency(Hz)': freq,
                   'Shunt resistance(Ohm)': shunt[switch_position],
                   'MTJ operating current(A)': MTJ_curr,
                   'MTJ signal amplitude(V)': MTJ_Vpp,
                   'HHC field amplitude(G)': HHC_Hpp,
                   'Sensitivity(%/G)': Sensitivity
                  }

    # Power off
    addr20.write(":OUTP OFF")
    addr19.write("APPL:DC DEF, DEF, 0V")

    print(addr10.query("SYST:ERR?"))
    print(addr19.query("SYST:ERR?"))
    print(addr20.query("SYST:ERR?"))
    
    return measurement

# Function ends

start = timeit.default_timer()
sensitivities = []
volts = [1, 2, 3, 4, 5]
for v in volts:
    sensitivities.append(sensitivity_measure(v, 95, 'Pos 2'))
    stop = timeit.default_timer()    
    print('Time: ', stop - start, 's')
    
print(sensitivities)
with open('Sensitivity.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, sensitivities[0].keys())
    writer.writeheader()
    writer.writerows(sensitivities)