import os
import sys
import pyvisa
import time
import timeit
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#import Instr_lib as instrlib
import device
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from GPIB_instruments import Agilent6613C_PowerSupply, Agilent2400_SourceMeter

class TransferCurve():
    
    # Initialize instruments and parameters
    def __init__(self, NPLC=0.03):
        # Default variables
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
        
        # Construct instrument objects
        self.x_address="GPIB0::5::INSTR"
        self.y_address="GPIB0::9::INSTR"
        self.sm_address="GPIB0::20::INSTR"
        self.NPLC=NPLC
        self.PowerSupply_X = Agilent6613C_PowerSupply(self.x_address)
        self.PowerSupply_Y = Agilent6613C_PowerSupply(self.y_address)
        self.SourceMeter = Agilent2400_SourceMeter(self.sm_address)
        
        # Initialize instrument objects
        self.PowerSupply_X.initialize()
        self.PowerSupply_Y.initialize()
        self.SourceMeter.initialize()
        self.SourceMeter.NPLC()
        
        self.my_path = os.path.dirname(os.path.abspath(__file__))
        #self.plotter = PlotCanvas()
    
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
    def output_on(self, x_onoff=True, y_onoff=False, sm_onoff=True):
        self.PowerSupply_X.output(x_onoff)
        self.PowerSupply_Y.output(y_onoff)
        self.SourceMeter.output(sm_onoff)
    
    # Power Supply params
    # (In gauss)
    def PS_params_gauss(self, start_gauss=None, stop_gauss=None, step_gauss=None, loop=None):
        # Default parameters 
        if start_gauss == None: self.start_gauss = self.default_gauss_start
        else: self.start_gauss = start_gauss
            
        if stop_gauss == None: self.stop_gauss = self.X_magnet_GPA
        else: self.stop_gauss = stop_gauss
            
        if step_gauss == None: self.step_gauss = self.a_to_g(self.default_curr_step)  
        else: self.step_gauss = step_gauss
        
        # Convert inputs in gausss to amps
        self.start_curr = self.g_to_a(self.start_gauss)
        self.stop_curr = self.g_to_a(self.stop_gauss)
        self.step_curr = self.g_to_a(self.step_gauss)
            
        if loop == None: self.loop = self.default_loop
        else: self.loop = loop
        
    # (In amps)
    def PS_params_amps(self, start_curr=None, stop_curr=None, step_curr=None, loop=None):
        # Default parameters 
        if start_curr == None: self.start_curr = self.g_to_a(self.default_gauss_start)
        else: self.start_curr = start_curr
            
        if stop_curr == None: self.stop_curr = self.g_to_a(self.X_magnet_GPA)
        else: self.stop_curr = stop_curr
        
        if step_curr == None: self.step_curr = self.g_to_a(self.default_curr_step)  
        else: self.step_curr = step_curr
        
        # Convert inputs in amps to gauss
        self.start_gauss = self.a_to_g(start_curr)
        self.stop_gauss = self.a_to_g(stop_curr)
        self.step_gauss = self.a_to_g(step_curr)
        
        if loop == None: self.loop = self.default_loop
        else: self.loop = loop
        
    # Power Supply sequence for one back and forth sweeping
    def PS_sweep_seq(self, start, stop, step):
        seq_asc = np.arange(start, stop, step)[0:-1]
        seq_desc = np.arange(stop, start, -step)[0:-1]
        return np.concatenate((seq_asc, seq_desc))
    
    # Entire Power Supply sequence
    def PS_curr_seq(self):
        seq_asc = np.arange(self.start_curr, self.start_curr, self.step_curr)
        seq_desc = np.arange(self.stop_curr, self.start_curr, -self.step_curr)
        
        seq_1 = np.concatenate((self.PS_sweep_seq(self.start_curr, self.stop_curr, self.step_curr), self.PS_sweep_seq(-self.start_curr, -self.stop_curr, -self.step_curr)))
        seq = []
        for i in range(self.loop):
            seq = np.concatenate((seq, seq_1))
        seq = np.concatenate((seq, seq_asc))
        return seq
    
    # Biasing field control
    def bias_y(self, bias_ON=True, bias_gauss=None):
        # Default parameters 
        if bias_gauss == None: self.bias_gauss = 0
        else: self.bias_gauss = bias_gauss
            
        if bias_ON == True:
            self.PowerSupply_Y.source_I(self.g_to_a(self.bias_gauss))
            self.PowerSupply_Y.output(True)
        elif bias_ON == False:
            self.PowerSupply_Y.output(False)
        else:
            raise Exception(f"TransferCurve: Invalid biasing field(gauss) input: {str(e)}")

    # Sourcemeter params
    def SM_MTJ_curr(self, MTJ_curr=None, pts_repeated=None, square_wave=None):
        # Default parameters 
        if MTJ_curr == None: self.MTJ_curr = self.default_MTJ_operating_curr  
        else: self.MTJ_curr = MTJ_curr
        if pts_repeated == None: pts_repeated = self.default_cycle_length  
        else: pts_repeated = pts_repeated
        if square_wave == None: square_wave = self.default_square_wave 
        else: self.square_wave = square_wave
        
        if square_wave == True:
            MTJ_curr_arr = np.repeat([self.MTJ_curr, -self.MTJ_curr],(pts_repeated))
        elif square_wave == False:
            MTJ_curr_arr = np.repeat(self.MTJ_curr, (pts_repeated))
        else:
            raise Exception(f"TransferCurve: Invalid current sample input: {str(e)}")
        return MTJ_curr_arr
    
    # Measure the votlage across the sample under one single magnetic field
    def measure_single_point(self, EM_curr):
        # Check compliance
        self.PowerSupply_X.compliance_level()
        
        # PS source and measure
        self.PowerSupply_X.source_I(EM_curr)
        curr_PS_read = self.PowerSupply_X.read_I()
        
        # SM source and measure
        volt_arr_SM_read = self.SourceMeter.read_buffer()
        
        # Calculate volt average
        if self.default_square_wave == True:
            volt_SM_read = (sum(volt_arr_SM_read[0::2]) - sum(volt_arr_SM_read[1::2])) / len(volt_arr_SM_read)
        else:
            volt_SM_read = sum(volt_arr_SM_read)/len(volt_arr_SM_read)
        return curr_PS_read, volt_SM_read
            
    def render_data(self, t, i, v, r):
        data = np.vstack((t, i, v, r)).T
        df = pd.DataFrame(data)
        df.to_csv(self.my_path + '/Data/Transfer curve Raw data max_G ' + str(self.stop_gauss) + ', Biasing_y ' + str(self.bias_gauss) + '.csv', index=False, header=False)

    
    
    def measure_transfer_curve(self, start_gauss=None, stop_gauss=None, step_gauss=None, loop=None,
                               MTJ_operating_curr=None, cycle_length=None, square_wave=None,
                               bias_gauss=None, bias_ON=False):
        # Volt Compliance
        self.PowerSupply_X.source_I(0.1)
        
        # Bias Y field
        self.bias_y(bias_ON, bias_gauss)
        
        # Create current sequence
        curr_input = self.SM_MTJ_curr(MTJ_operating_curr, cycle_length, square_wave)
        
        # PS initialize
        self.PS_params_gauss(start_gauss, stop_gauss, step_gauss, loop)
        
        # SM set input value
        self.SourceMeter.source_list_I(curr_input)
        # Preloop variables
        
        seq = self.PS_curr_seq()
        curr_arr = []
        volt_arr = []
        resist_arr = []
        time_arr = []
        # Start plotting
        
        # Start timing
        start = timeit.default_timer()
        
        # Execute loop 
        self.output_on()
        for i in seq:
            curr_out, volt_out = self.measure_single_point(i)
            
            # Concatenate data
            curr_arr.append(curr_out)
            volt_arr.append(volt_out)
            
            # Collect time stamps
            time_stamp = timeit.default_timer()
            time_arr.append(time_stamp-start)
            
            # Calculate resistance results
            resist = volt_out/self.MTJ_curr
            resist_arr.append(resist)
            # Plot real-time 
            
        # Render data 
        self.render_data(curr_arr, volt_arr, resist_arr, time_arr)
        # Final plot
        
        self.output_on(False, False, False)
        return time_arr, curr_arr, volt_arr, resist_arr
    
    
    
    

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig, self.axes = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        
    def read_data(self, tc, file_name="Transfer curve Raw data max_G 132.3129, Biasing_y 0.csv"):
        self.file_name = file_name
        data = np.loadtxt(tc.my_path + '/Data/' + file_name, delimiter=",", dtype=float)
        return data[:, 0], data[:, 1], data[:, 2], data[:, 3]
        
    def plot_scatter(self, x, y):
        plt.scatter(x, y, s=1)
        self.axes.set(xlabel='Magnetic field (G)', ylabel='Resistance (Ohm)',
                title='Magnetic field vs Resistance')
        self.axes.grid()
        #plt.title(self.file_name)
        plt.show()
        
    #def plot_point_and_update():


class LinePlotterApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # Widgets for left side
        slope_label = QLabel('Slope:')
        self.slope_input = QLineEdit()

        intercept_label = QLabel('Intercept:')
        self.intercept_input = QLineEdit()

        go_button = QPushButton('Go')
        go_button.clicked.connect(self.plot_line)

        # Layout for left side
        left_layout = QGridLayout()
        left_layout.addWidget(slope_label, 0, 0)
        left_layout.addWidget(self.slope_input, 0, 1, 1, 2)
        left_layout.addWidget(intercept_label, 1, 0)
        left_layout.addWidget(self.intercept_input, 1, 1, 1, 2)
        left_layout.addWidget(go_button)

        # Widgets for right side
        self.plot_canvas = PlotCanvas(self)

        # Layout for right side
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.plot_canvas)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Line Plotter')

    def plot_line(self):
        try:
            slope = float(self.slope_input.text())
            intercept = float(self.intercept_input.text())
        except ValueError:
            print("Invalid input. Please enter numeric values for slope and intercept.")
            return

        self.plot_canvas.plot_line(slope, intercept)

if __name__ == "__main__":
    try:
        #app = QApplication(sys.argv)
        #window = LinePlotterApp()
        TC = TransferCurve()
        '''
        Transfer Curve measurement parameters:
        
        start_gauss (float):            default = 0, 
        stop_gauss (float):             default = 132.3129(X_magnet_GPA),
        step_gauss (float):             default = 0.3 mA * 132.3129 GPA = 0.0397 G = 3.97 µT, 
        loop (int):                     default = 1, 
        MTJ_operating_curr (float):     default = 0.001 mA, 
        cycle_length (float):           default = 2, 
        square_wave (boolean):          default = False, 
        bias_gauss (float):             default = 0, 
        bias_ON (float):                default = 0
        '''
        #T, I, V, R = TC.measure_transfer_curve(loop=3)
        
        curve = PlotCanvas()
        T, I, V, R = curve.read_data(TC)
        print(I)
        print(V)
        print(R)
        print(T)
        curve.plot_scatter(I, R)
        #window.show()
    except Exception as e:
        print(f"Error: {str(e)}")