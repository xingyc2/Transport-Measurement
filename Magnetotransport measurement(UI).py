import os
import pyvisa
import time
import timeit
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#import Instr_lib as instrlib
import device
from GPIB_instruments import Agilent6613C_PowerSupply, Agilent2400_SourceMeter

class TransferCurve():
    self.X_magnet_GPA = 132.3129
    self.Y_magnet_GPA = 129.76684
    self.max_curr_PS = 1
    
    def __init__(self):
        #super().__init__()
        self.initialize()
    
    def a_to_g(self, a, GPA='X'):
        if GPA == 'X':
            return a*self.X_magnet_GPA
        elif GPA == 'Y':
            return a*self.X_magnet_GPA
    
    def g_to_a(self, g, GPA='Y'):
        if GPA == 'X':
            return g/self.Y_magnet_GPA
        elif GPA == 'Y':
            return g/self.Y_magnet_GPA

    def initialize(self, x_address="GPIB0::5::INSTR", y_address="GPIB0::9::INSTR", sm_address="GPIB0::20::INSTR", NPLC=0.03):
        PowerSupply_X = Agilent6613C_PowerSupply(x_address)
        PowerSupply_Y = Agilent6613C_PowerSupply(y_address)
        SourceMeter = Agilent2400_SourceMeter(sm_address)

        PowerSupply_X.initialize()
        PowerSupply_Y.initialize()
        SourceMeter.initialize()
        SourceMeter.NPLC()
    
    def output_on(self, x_onoff=True, y_onoff=False, sm_onoff=True)
        PowerSupply_X.output(x_onoff)
        PowerSupply_Y.output(y_onoff)
        SourceMeter.output(sm_onoff)
        
    def sweep_params_gauss(self, start_gauss=0, stop_gauss=self.X_magnet_GPA, step_gauss=0.0003*X_magnet_GPA, loop=1):
        self.start_gauss = start_gauss
        self.stop_gauss = stop_gauss
        self.step_gauss = step_gauss
        self.start_curr = start_gauss/X_magnet_GPA
        self.stop_curr = stop_gauss/X_magnet_GPA
        self.step_curr = step_gauss/X_magnet_GPA
        slef.loop = loop
        
    def sweep_params_amps(self, start_curr=0, stop_curr=self.max_curr_PS, step_curr=0.0003, loop=1):
        self.start_curr = start_curr
        self.stop_curr = stop_curr
        self.step_curr = step_curr
        self.start_gauss = start_curr*X_magnet_GPA
        self.stop_gauss = stop_curr*X_magnet_GPA
        self.step_gauss = step_curr*X_magnet_GPA
        slef.loop = loop

    def curr_sample(self, curr_sample=0.001, pts_repeated=2, square_wave=False):
        try:
            if square_wave == True:
                self.curr_sample_arr = np.repeat([curr_sample, -curr_sample],(pts_repeated))
            elif square_wave == False:
                self.curr_sample_arr = np.repeat(curr_sample, (pts_repeated))
            else:
                raise Exception()
        except Exception as e:
            raise Exception(f"TransferCurve: Invalid current sample input: {str(e)}")
            
    '''
    def bias_y_arr(self, bias_ON=False):
        try:
            PowerSupply_Y.output(bias_ON)
        except Exception as e:
            raise Exception(f"TransferCurve: Invalid biasing Y field input: {str(e)}")
        
    def bias_y_arr(self, bias_ON=True, y_arr_gauss):
        try:
            if bias_ON == True:
                PowerSupply_Y.output(bias_ON)
                
            else:
                PowerSupply_Y.output(False)
        except Exception as e:
            raise Exception(f"TransferCurve: Invalid biasing Y field input: {str(e)}")
        '''
    
    def 
    
    
    

# Sweep array parameter setup
stop_gauss = X_magnet_GPA*1
step_gauss = X_magnet_GPA*0.0003
min_curr = start_gauss/X_magnet_GPA
max_curr = stop_gauss/X_magnet_GPA
step = step_gauss/X_magnet_GPA
loop = 1
# Square wave array
curr_sample = 0.001
pts_per_hfcycle = 1
compliance = 50
# Array of different magnitudes of biasing field
bias_y_arr_gauss = [-10]
bias_y_arr = np.array(bias_y_arr_gauss) / Y_magnet_GPA
bias_ON = True
live_display = 'DISABLED'                  # Options of 'DISABLED', 'WHOLE', 'TRACE', and 'WHOLE and TRACE'
                                        # for observing the transfer curve measurement

FourProbe.NPLC(0.03)



X_field.output()
Y_field.output()
FourProbe.output()
