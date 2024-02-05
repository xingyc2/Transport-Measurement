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
    
    # Initialize instruments and parameters
    def __init__(self, NPLC=0.03):
        self.X_magnet_GPA = 132.3129
        self.Y_magnet_GPA = 129.76684
        self.max_curr_PS = 1
        self.default_loop = 1
        self.default_curr_step = 0.0003
        self.default_gauss_start = 0
        self.default_gauss_stop = self.X_magnet_GPA
        self.default_MTJ_operating_curr = 0.001
        self.default_cycle_length = 2
        self.default_bias_gauss = 0
        self.default_square_wave = False
        
        self.x_address="GPIB0::5::INSTR"
        self.y_address="GPIB0::9::INSTR"
        self.sm_address="GPIB0::20::INSTR"
        self.NPLC=NPLC
        self.PowerSupply_X = Agilent6613C_PowerSupply(x_address)
        self.PowerSupply_Y = Agilent6613C_PowerSupply(y_address)
        self.SourceMeter = Agilent2400_SourceMeter(sm_address)

        self.PowerSupply_X.initialize()
        self.PowerSupply_Y.initialize()
        self.SourceMeter.initialize()
        self.SourceMeter.NPLC()
        
        self.plotter = PlotCanvas()
    
    # Ampere/Gauss conversion
    def a_to_g(self, a, GPA='X'):
        if GPA == 'X':
            return a*self.X_magnet_GPA
        elif GPA == 'Y':
            return a*self.X_magnet_GPA
            
    # Gauss/Ampere conversion
    def g_to_a(self, g, GPA='Y'):
        if GPA == 'X':
            return g/self.Y_magnet_GPA
        elif GPA == 'Y':
            return g/self.Y_magnet_GPA
    
    # Output controls
    def output_on(self, x_onoff=True, y_onoff=False, sm_onoff=True)
        self.PowerSupply_X.output(x_onoff)
        self.PowerSupply_Y.output(y_onoff)
        self.SourceMeter.output(sm_onoff)
    
    # Power Supply params
    # (In gauss)
    def PS_params_gauss(self, start_gauss=self.default_gauss_start, stop_gauss=self.X_magnet_GPA, step_gauss=self.a_to_g(self.default_curr_step), loop=self.default_loop):
        self.start_gauss = start_gauss
        self.stop_gauss = stop_gauss
        self.step_gauss = step_gauss
        self.start_curr = self.g_to_a(start_gauss)
        self.stop_curr = self.g_to_a(stop_gauss)
        self.step_curr = self.g_to_a(step_gauss)
        self.loop = loop
        
    # (In amps)
    def PS_params_amps(self, start_curr=self.default_curr_start, stop_curr=self.max_curr_PS, step_curr=self.default_curr_step, loop=self.default_loop):
        self.start_curr = start_curr
        self.stop_curr = stop_curr
        self.step_curr = step_curr
        self.start_gauss = self.a_to_g(start_curr)
        self.stop_gauss = self.a_to_g(stop_curr)
        self.step_gauss = self.a_to_g(step_curr)
        slef.loop = loop
        
    # Power Supply sequence for one back and forth sweeping
    def PS_sweep_seq(start, stop, step):
        seq_asc = np.arange(start, stop, step)[0:-1]
        seq_desc = np.arange(stop, start, -step)[0:-1]
        return np.concatenate((seq_asc, seq_desc))
    
    #
    def PS_curr_seq(self):
        seq_asc = np.arange(self.min_curr, self.max_curr, self.step)
        seq_desc = np.arange(self.max_curr, self.min_curr, -self.step)
        seq_1 = np.concatenate((self.PS_sweep_seq(self.min_curr, self.max_curr, self.step), self.PS_sweep_seq(-self.min_curr, -self.ax_curr, -self.step)))
        seq = []
        for i in range(loop):
            seq = np.concatenate((seq, seq_1))
        seq = np.concatenate((seq, seq_asc))
        return seq
    
    # Biasing field control
    def bias_y(self, bias_ON=True, bias_gauss=default_bias_gauss):
        if bias_ON == True:
            self.PowerSupply_Y.source_I(bias_value)
            self.PowerSupply_Y.output(True)
        elif bias_ON == False:
            self.PowerSupply_Y.output(False)
        else:
            raise Exception(f"TransferCurve: Invalid biasing field(gauss) input: {str(e)}")

    # Sourcemeter params
    def SM_curr_sample(self, curr_sample=self.default_MTJ_operating_curr, pts_repeated=self.default_cycle_length, square_wave=self.default_square_wave):
        if square_wave == True:
            MTJ_curr_arr = np.repeat([curr_sample, -curr_sample],(pts_repeated))
        elif square_wave == False:
            MTJ_curr_arr = np.repeat(curr_sample, (pts_repeated))
        else:
            raise Exception(f"TransferCurve: Invalid current sample input: {str(e)}")
        return MTJ_curr_arr
    
    
    def measure_single_point(self, EM_curr):
        PowerSupply_X.compliance_level(EM_curr)
        PowerSupply_X.source_I(EM_curr)
        curr_PS_read = PowerSupply_X.read_I()
        print(curr_PS_read)
        volt_arr_SM_read = SourceMeter.read_buffer()
        print(volt_arr_SM_read)
        if self.default_square_wave == False:
            volt_SM_read = sum(volt_arr_SM_read)/len(volt_arr_SM_read)
        else:
            volt_SM_read = (sum(volt_arr_SM_read[0::2]) - sum(volt_arr_SM_read[1::2])) / len(volt_arr_SM_read)
        return curr_PS_read, volt_SM_read
            
    def 


    
    
    
    def measure_transfer_curve(self, start_gauss=self.default_gauss_start, stop_gauss=self.X_magnet_GPA, step_gauss=self.a_to_g(self.default_curr_step), loop=self.default_loop,
                               MTJ_operating_curr=self.default_MTJ_operating_curr, cycle_length=default_cycle_length,
                               bias_gauss=default_bias_gauss, bias_ON=False):
        # Volt Compliance
        PowerSupply_X.source_I(0.1)
        
        # Bias Y field
        self.bias_y(0, False)
        
        # Create current sequence
        curr_input = self.SM_curr_sample()
        
        # PS initialize
        PS_params_gauss()
        
        # SM set input value
        SourceMeter.source_list_I(SM_curr_sample())
        # Preloop variables
        
        seq = self.PS_curr_seq()
        curr_arr = []
        # Start plotting
        
        # Start timing
        start = timeit.default_timer()
        # Execute loop 
        
            # Check compliance
            # PS source and measure
            # SM source and measure
            # Concatenate data
            # Collect time stamps
            # Calculate resistance results
            # Plot real-time 
        # Stop timing 
        # Render data 
        # Final plot
        
    
    
    
    
    
    
    
    
    def bias_y(self, y_gauss, bias_ON=True):
        if bias_ON == True:
            PowerSupply_Y.output(bias_ON)
            '''
            '''
        else:
            PowerSupply_Y.output(False)
    
    def 
    
    
    
class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig, self.axes = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(fig)
        self.setParent(parent)
        
    def plot_line(self, slope, intercept):
        self.axes.clear()
        x = np.linspace(-10, 10, 100)
        y = slope * x + intercept
        self.axes.polt(x, y)
        _addressself.axes.set.xlalbel
        
    #def plot_point_and_update():
