import os
import pyvisa
import time
import timeit
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import Instr_lib as instrlib

my_path = os.path.dirname(os.path.abspath(__file__))

rm = pyvisa.ResourceManager()
print(rm.list_resources())

# Initialize instrument object using pyvisa
addr5 = rm.open_resource('GPIB0::5::INSTR')
addr9 = rm.open_resource('GPIB0::9::INSTR')
addr20 = rm.open_resource('GPIB0::20::INSTR')

# Agilent 6613C is the power supply for the electromagnet, which sweeps from 0A to 1A, 0A to -1A 
# back and forth of each. (in increments of 0.3mA at default)
# Agilent 2400 is the sourcemeter which sends square wave(with amplitude of 1mA at default) at each discrete
# level of 

# Agilent 6613C initalization
addr5.write("*RST")
addr5.write("*CLS")
addr5.write("SENSe:SWEep:POINts 256")              # Reading speed control

addr9.write("*RST")
addr9.write("*CLS")
addr9.write("SENSe:SWEep:POINts 256")              # Reading speed control

# Agilent 2400 autozero
zero2400 = False
if (zero2400 == True):
    addr20.write("SYST:AZER ON")
    
# Agilent 2400 initalization
addr20.write('*RST')
addr20.write("SOUR:FUNC CURR")
addr20.write("SENS:FUNC \"VOLT\"")
addr20.write("SOUR:CURR:MODE LIST")
addr20.write("SOUR:CURR:RANGe 0.001")
#addr20.write("SENS:VOLT:PROT 5")
#addr20.write("SENS:CURR:PROT 0.004")
addr20.write("SENS:VOLT:RANG 10")
addr20.write("FORM:ELEM VOLT")

# Output ON
addr5.write("OUTP 1")
addr9.write("OUTP 1")
addr20.write("OUTP ON")

# Sweep array parameter setup
X_magnet_GPA = 132.3129
Y_magnet_GPA = 129.76684
start_gauss = 0
stop_gauss = X_magnet_GPA*1
step_gauss = X_magnet_GPA*0.0003


addr20.write("NPLC 0.03")              # Reading speed control
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

# Plot figure dimensions
diagram_bottom = 2150
diagram_top = 5400
diagram_left = -133
diagram_right = 133

def measure_transfer_curve(X_field, Y_field, min_curr, max_curr, step, loop, curr_sample, compliance, bias_y, bias_ON, live_display):
    curr_sample_arr = np.repeat([curr_sample, -curr_sample],(pts_per_hfcycle))
    X_field.write("VOLT " + str(compliance))
    
    
    # Biasing field in y-axis
    if bias_y < 0:
        Y_field.write("OUTP:REL ON")
        Y_field.write("OUTP:REL:POL REV")
    else:
        Y_field.write("OUTP:REL ON")
        Y_field.write("OUTP:REL:POL NORM") 
    if bias_ON == True:
        Y_field.write("VOLT 51")
        Y_field.write("CURR " + str(abs(bias_y)))
    else:
        Y_field.write("OUTP 0")


    # Create sourcemeter command
    curr_input = ''
    curr_input += str(curr_sample)
    for i in range(pts_per_hfcycle-1):
        curr_input += ','+str(curr_sample)
    for i in range(pts_per_hfcycle):
        curr_input += ','+str(-curr_sample)

    # Sweeping current array
    seq_asc = np.arange(min_curr, max_curr, step)
    seq_desc = np.arange(max_curr, min_curr, -step)
    seq_1 = np.concatenate((instrlib.sweep_seq(min_curr, max_curr, step), instrlib.sweep_seq(-min_curr, -max_curr, -step)))
    seq = []
    for i in range(loop):
        seq = np.concatenate((seq, seq_1))
    seq = np.concatenate((seq, seq_asc))

    # Input a signal array of current    seq, seq,
    addr20.write("SOUR:LIST:CURR " + curr_input)
    addr20.write("TRIG:COUN " + str(pts_per_hfcycle*2))

    # Pre
    cycle_count = 0
    volt_arr = []
    X_gauss_arr = []
    curr_arr = []
    resist_arr = []
    time_arr = []
    relay = 1

    # Plotting
    fig = plt.figure(figsize=(12,9), dpi=100)
    if live_display == 'WHOLE' or live_display == 'TRACE' or live_display == 'DISABLED':
        ax1 = fig.subplots()
        dots, = ax1.plot(X_gauss_arr, resist_arr, 'k.', markersize=3)
    elif live_display == 'WHOLE and TRACE':
        (ax1, ax2) = fig.subplots(2, 1)
        dots, = ax1.plot(X_gauss_arr, resist_arr, 'k.', markersize=3)
        dots2, = ax2.plot(X_gauss_arr, resist_arr, 'k.', markersize=3)
    #plt.show()
    
    # Start timing
    start = timeit.default_timer()

    # Execution loop
    for i in seq:
        # Agilent 6613C Relay function
        if (i < 0) and (relay == 1):
            X_field.write("OUTP:REL ON")
            X_field.write("OUTP:REL:POL REV")
            relay = -1
            print('relay')
            time.sleep(.3)
        elif (i > 0) and (relay == -1):
            X_field.write("OUTP:REL ON")
            X_field.write("OUTP:REL:POL NORM")
            relay = 1
            time.sleep(.3)
        cycle_count += 1
        
        if (abs(i) > 0.015) and (compliance != 51):
            X_field.write("VOLT 51")
            compliance = 51
            time.sleep(.3)
            #time.sleep(.1)
        elif (abs(i) > 0.001) and (abs(i) < 0.015) and (compliance != 1):
            X_field.write("VOLT 1")
            compliance = 1
            time.sleep(.3)
            #time.sleep(.1)
        elif (abs(i) < 0.001) and (compliance != 0.05):
            X_field.write("VOLT 0.05")
            compliance = 0.05
            time.sleep(.3)
            #time.sleep(.1)
        
        # Agilent 6613C output and measure the current to the electromagnet
        curr = relay*(float(X_field.query("CURR " + str(abs(i)) + ";MEAS:CURR?")))
        curr_arr.append(curr)
        X_gauss = curr*X_magnet_GPA
        X_gauss_arr.append(X_gauss)
        
        # Agilent 2400 measure and read voltage over the sample(:INIT and :FETCH? are combined in :READ?)
        cycle = addr20.query("READ?")
        
        # Concatenate all data in one line, separated with ',' and remove all '\n'
        cycle = instrlib.str_float(cycle[:len(cycle)-1])           # Turn string reading into a list of float
        volt = (np.sum(cycle[0:pts_per_hfcycle])-np.sum(cycle[pts_per_hfcycle:pts_per_hfcycle*2]))/(pts_per_hfcycle*2)
        volt_arr.append(volt)

        # Collect time stamps
        time_stamp = timeit.default_timer()
        time_arr.append(time_stamp-start)
        
        # Collect resistance results
        resist = volt/curr_sample
        resist_arr.append(resist)
        
        # Plot real-time diagram
        if live_display != 'DISABLED':
            if live_display == 'TRACE':
                ax1.set_xlim(left=X_gauss-step_gauss*100, right=X_gauss+step_gauss*100)
                ax1.set_ylim(bottom=resist*0.9, top=resist*1.1)
                dots.set_xdata(X_gauss_arr)
                dots.set_ydata(resist_arr)
            elif live_display == 'WHOLE':
                ax1.set_xlim(left=diagram_left, right=diagram_right)
                ax1.set_ylim(bottom=diagram_bottom, top=diagram_top)
                dots.set_xdata(X_gauss_arr)
                dots.set_ydata(resist_arr)
            elif live_display == 'WHOLE and TRACE':
                ax1.set_xlim(left=X_gauss-step_gauss*100, right=X_gauss+step_gauss*100)
                ax1.set_ylim(bottom=resist*0.9, top=resist*1.1)
                ax2.set_xlim(left=diagram_left, right=diagram_right)
                ax2.set_ylim(bottom=diagram_bottom, top=diagram_top)
                dots.set_xdata(X_gauss_arr)
                dots.set_ydata(resist_arr)
                dots2.set_xdata(X_gauss_arr)
                dots2.set_ydata(resist_arr)
            
            fig.canvas.draw()
            fig.canvas.flush_events()
        #fig.show()
        #plt.close()
        
    # Stop timing
    stop = timeit.default_timer()    
    print('Time: ', stop - start, 's')
    print("Data points: ", len(seq))
    print('Time per measurement: ', str((stop - start)/(len(seq))*1000), 'ms')


    

    # Write output data in spread sheet
    data = np.vstack((time_arr, seq, X_gauss_arr, resist_arr)).T
    df = pd.DataFrame(data)
    df.to_csv(my_path + '/Data/Transfer curve Raw data max_G ' + str(stop_gauss) + ', Biasing_y ' + str(bias_y) + '.csv', index=False, header=False)

    # Final plot
    ax1.scatter(X_gauss_arr, resist_arr, s=1)
    ax1.set(xlabel='Magnetic field(G)', ylabel='Resistance(Ohm)',
       title='Resistance vs Magnetic Field')
    ax1.set_xlim(left=diagram_left, right=diagram_right)
    ax1.set_ylim(bottom=diagram_bottom, top=diagram_top)
    ax1.grid()
    fig.savefig(my_path + '/Data/Transfer curve max_G ' + str(stop_gauss) + ', Biasing_y ' + str(bias_y) + '.png')
    fig.show()
    if live_display == 'DISABLED':
        ax1.set_xlim(left=diagram_left, right=diagram_right)
        ax1.set_ylim(diagram_bottom, top=diagram_top)
        ax1.plot(X_gauss_arr, resist_arr, 'k.', markersize=1)
        #plt.show()



# Start Operation
for bias_ys in bias_y_arr:
    measure_transfer_curve(addr5, addr9, min_curr, max_curr, step, loop, curr_sample, compliance, bias_ys, bias_ON, live_display)

# Output OFF
addr20.write("OUTP OFF")
addr9.write("OUTP 0")
addr5.write("OUTP 0")

# Error messages
error5 = addr5.query("SYST:ERR?")
print(error5)
error9 = addr9.query("SYST:ERR?")
print(error5)
error20 = addr20.query("STAT:QUE?")
print(error20)


# Show runtime plot
'''
time_arr = np.array(time_arr) - time_arr[0]
plt.plot(range(time_arr.size), np.divide(time_arr, range(time_arr.size)))
plt.show()

'''


