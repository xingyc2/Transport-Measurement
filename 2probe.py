import os
import pyvisa
import time
import timeit
import numpy as np
import matplotlib.pyplot as plt
from sigfig import round
import pandas as pd
from GPIB_instruments import Agilent2400_SourceMeter

'''
class Two_Probe():
    def __init__(self, address='GPIB0::20::INSTR'):
        self.address = address
        self.SourceMeter = Agilent2400_SourceMeter(address)
        
    def sweep_list(self, start, stop, step):
        arr = np.arange(start, stop, step)
        curr = ','.join([str(round(i, sigfigs=2)) for i in np.divide([i for i in range(0, 11)], 10000)])
        return arr
        
    def measure(self, start, stop, step):
        pass
        
        
if __name__ == "__main__":
    try:
        #meas = Two_Probe()
        #meas.sweep_list(0, 0.001, 0.000005)
    
        arr = np.arange(0, 0.001, 0.000005)
        print(arr)
    
    except Exception as e:
        print(f"Error: {str(e)}")
'''

SM = Agilent2400_SourceMeter('GPIB0::20::INSTR')
        
def sweep_list(start, stop, step):
    arr = np.arange(start, stop, step)
    curr = ','.join([str(round(i, sigfigs=2)) for i in arr])
    return curr

#def measure(start, stop, step):
#    pass
curr = sweep_list(0, 0.001, 0.0001)

print(curr)

SM.initialize()
SM.NPLC()
SM.source_list_I(curr)
SM.output(True)
t0 = timeit.default_timer() 
print(SM.get_values())
t1 = timeit.default_timer() 

SM.output()

print("Time: ", str(t1-t0))