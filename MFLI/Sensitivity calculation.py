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
shuntVolt = float(addr10.query("MEAS:VOLT:AC?"))
shunt = shunt10k
HHC_curr = shuntVolt/shunt*np.sqrt(2)
GPA = X_HHC_GPA
Hfield = HHC_curr * GPA
dc_component = float(addr26.query('F0')[4:])
print('Shunt voltage: ', shuntVolt)
print('H field calculated: ', Hfield)
print('DC component: ', dc_component)
r_ave = np.average(data['r']['value'])
MTJ_Vpk = r_ave*np.sqrt(2)
percent_delta = MTJ_Vpk/dc_component
Sensitivity = percent_delta/Hfield*100
print("Sensitivity: ", str(Sensitivity), "%/G")

# Power off
addr20.write(":OUTP OFF")
addr19.write("APPL:DC DEF, DEF, 0V")

print(addr10.query("SYST:ERR?"))
print(addr19.query("SYST:ERR?"))
print(addr20.query("SYST:ERR?"))