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
    
    def __init__(self):
        self.X_magnet_GPA = 132.3129
        self.Y_magnet_GPA = 129.76684
        self.max_curr_PS = 1
        
        x_address="GPIB0::5::INSTR"
        y_address="GPIB0::9::INSTR"
        sm_address="GPIB0::20::INSTR"
        NPLC=0.03
        self.PowerSupply_X = Agilent6613C_PowerSupply(x_address)
        self.PowerSupply_Y = Agilent6613C_PowerSupply(y_address)
        self.SourceMeter = Agilent2400_SourceMeter(sm_address)

        self.PowerSupply_X.initialize()
        self.PowerSupply_Y.initialize()
        self.SourceMeter.initialize()
        self.SourceMeter.NPLC()
        
        self.plotter = PlotCanvas()
    
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
    
    def output_on(self, x_onoff=True, y_onoff=False, sm_onoff=True)
        self.PowerSupply_X.output(x_onoff)
        self.PowerSupply_Y.output(y_onoff)
        self.SourceMeter.output(sm_onoff)
        
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

    def SM_curr_sample(self, curr_sample=0.001, pts_repeated=2, square_wave=False):
        if square_wave == True:
            self.curr_sample_arr = np.repeat([curr_sample, -curr_sample],(pts_repeated))
        elif square_wave == False:
            self.curr_sample_arr = np.repeat(curr_sample, (pts_repeated))
        else:
            raise Exception(f"TransferCurve: Invalid current sample input: {str(e)}")
        curr_input = ''
        for i in self.curr_sample_arr:
            curr_input += ','+str(curr_sample)
        return curr_input[1:]
    
    def bias_y(self, bias_gauss=0, bias_ON=False):
        if bias_ON == True:
            self.PowerSupply_Y.source_I(bias_value)
            self.PowerSupply_Y.output(True)
        elif bias_ON == False:
            self.PowerSupply_Y.output(False)
        else:
            raise Exception(f"TransferCurve: Invalid biasing field(gauss) input: {str(e)}")
    
    def sweep_seq(start, stop, step):
        seq_asc = np.arange(start, stop, step)[0:-1]
        seq_desc = np.arange(stop, start, -step)[0:-1]
        return np.concatenate((seq_asc, seq_desc))
    
    def curr_seq(self):
        seq_asc = np.arange(self.min_curr, self.max_curr, self.step)
        seq_desc = np.arange(self.max_curr, self.min_curr, -self.step)
        seq_1 = np.concatenate((self.sweep_seq(self.min_curr, self.max_curr, self.step), self.sweep_seq(-self.min_curr, -self.ax_curr, -self.step)))
        seq = []
        for i in range(loop):
            seq = np.concatenate((seq, seq_1))
        seq = np.concatenate((seq, seq_asc))
        return seq
    
    def measure_single_point(self, curr):
        PowerSupply_X.source_I(curr)
        curr_read = PowerSupply_X.read_I(True)
        print(curr_read)
        curr_arr.append(curr_read)
    
    
    
    
    
    def measure_transfer_curve(MTJ_operating_current, bias_gauss, bias_ON):
        # Volt Compliance
        
        # Bias Y field
        self.bias_y(bias_gauss, bias_ON)
        
        # Create current sequence
        curr_input = self.SM_curr_sample()
        # SM set input value
        seq = self.curr_seq()
        # Preloop variables
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
