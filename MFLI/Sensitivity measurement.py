import pyvisa
import time
import timeit
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from zhinst.toolkit import Session
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

session = Session('localhost')
device = session.connect_device('dev7173')

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

    device.demods[0].sample.subscribe()
    time.sleep(1)
    device.demods[0].sample.unsubscribe()
    poll_result = session.poll()
    demod_sample = poll_result[device.demods[0].sample]

    print(demod_sample)
    r = np.sqrt(np.square(demod_sample["x"]) + np.square(demod_sample["y"]))    
    
    daq.set(f"/{device_id}/extrefs/0/enable", 1)
    daq.set(f"/{device_id}/demods/1/adcselect", 8)
    daq.set(f"/{device_id}/sigins/0/ac", 1)
    daq.set(f"/{device_id}/demods/0/order", lowpass_order)
    daq.set(f"/{device_id}/demods/0/order", lowpass_order)

    daq.set(f"/{device_id}/sigins/0/autorange", 1)
    time.sleep(0.2)
    daq.set(f"/{device_id}/sigins/0/autorange", 1)
    daq.set(f"/{device_id}/demods/0/sinc", 1)

    daq.set(f"/{device_id}/demods/0/enable", 1)

    

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
