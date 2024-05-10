from pymeasure.instruments.keithley import Keithley2400
from pymeasure.instruments.agilent import Agilent6613C
from pymeasure.log import console_log
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Procedure, Results, IntegerParameter, FloatParameter, BooleanParameter, Parameter, unique_filename
from time import sleep
import numpy as np
import sys
import tempfile
import timeit

from pymeasure.log import log, console_log

class SensitivityProcedure(Procedure):
    
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
    
    # Default parameters
    X_magnet_GPA = 132.3129
    Y_magnet_GPA = 129.76684
    default_max_gauss = X_magnet_GPA
    default_step = 0.0003
    default_MTJ_operating_current = 0.001
    default_MTJ_operating_current_range = 0.002
    default_MTJ_operating_voltage_range = 20
    default_NPLC = 0.01
    default_voltage_range = 6
    
    # Boolean parameter for choosing transfer curve inputs in gauss or amp
    gauss_or_amp = BooleanParameter('Choose input in gauss or in amp. True: gauss; False: amp.', default=True)
    
    # Inputs in gauss
    # The magnetic field will start from the starting magnitude to the maximum, then starts to loop from 
    # the maximum to the minimum and back and forth.
    start_gauss = FloatParameter('Initial magnetic field strength', units='G', default=0, group_by='gauss_or_amp', group_condition=True)
    min_gauss = FloatParameter('Minimum magnetic field strength', units='G', default=-default_max_gauss, group_by='gauss_or_amp', group_condition=True)
    max_gauss = FloatParameter('Maximum magnetic field strength', units='G', default=default_max_gauss, group_by='gauss_or_amp', group_condition=True)
    step_gauss = FloatParameter('Magnetic field strength increment', units='G', default=default_step*default_max_gauss, group_by='gauss_or_amp', group_condition=True)
    
    # Inputs in amp
    start_amp = FloatParameter('Initial magnetic field strength', units='A', default=0, group_by='gauss_or_amp', group_condition=False)
    min_amp = FloatParameter('Minimum magnetic field strength', units='A', default=-1, group_by='gauss_or_amp', group_condition=False)
    max_amp = FloatParameter('Maximum magnetic field strength', units='A', default=1, group_by='gauss_or_amp', group_condition=False)
    step_amp = FloatParameter('Magnetic field strength increment', units='A', default=default_step, group_by='gauss_or_amp', group_condition=False)
    
    # Number of loops
    loop = IntegerParameter('Number of hysteresis loops', default=1)
    
    # Biasing field control
    bias_ON = BooleanParameter('Biasing field switch. False: OFF; True: ON.', default=False)
    bias_gauss = FloatParameter('Biasing field strength', units='G', default=0, group_by='bias_ON', group_condition=True)
    
    # Other parameters
    toggle = BooleanParameter('Other parameters.', default=False)
    cycle_length = FloatParameter('Points for one measurement', default=1, group_by='toggle', group_condition=True)
    MTJ_operating_curr = FloatParameter('MTJ sample operating current', units='A', default=default_MTJ_operating_current, group_by='toggle', group_condition=True)
    square_wave = IntegerParameter('0: Only positive current; 1: Positive and negative current', default=1, group_by='toggle', group_condition=True)
    NPLC = FloatParameter('NPLC(fast:0.01 - slow:10) Measurement speed:', default=default_NPLC, group_by='toggle', group_condition=True)
    voltage_range = FloatParameter('Voltage measurement range', units='V', default=default_voltage_range, group_by='toggle', group_condition=True)
    
    # List of data columns
    DATA_COLUMNS = ['Time (s)', 'Current (A)', 'Voltage (V)', 'Magnetic Field (G)', 'Resistance (V/A)']

    '''
    Inheriting the procedure startup function. 
    It contains initialization of the Keithley 2400 Sourcemeter, two Agilent6613C PowerSupplies.
    '''
    def startup(self):
        log.info("Connecting and configuring the instrument")
        
        # Initialization of the Keithley 2400 Sourcemeter
        self.SourceMeter = Keithley2400("GPIB::20")
        self.SourceMeter.reset()
        self.SourceMeter.use_front_terminals()
        sleep(0.1)  # wait here to give the instrument time to react
        self.SourceMeter.stop_buffer()
        self.SourceMeter.disable_buffer()
        
        # Initialization of the Agilent6613C PowerSupply.
        self.PowerSupply_X = Agilent6613C("GPIB::5")
        self.PowerSupply_X.reset()
        
        # Initialization of the Agilent6613C PowerSupply.
        self.PowerSupply_Y = Agilent6613C("GPIB::9")
        self.PowerSupply_Y.reset()
        
    # Convert the input in gauss to in amp
    def to_amp(self):
        self.start_amp = self.g_to_a(self.start_gauss)
        self.min_amp = self.g_to_a(self.min_gauss)
        self.max_amp = self.g_to_a(self.max_gauss)
        self.step_amp = self.g_to_a(self.step_gauss)

    # Convert the input in amp to in gauss
    def to_gauss(self):
        self.start_gauss = self.a_to_g(self.start_amp)
        self.min_gauss = self.a_to_g(self.min_amp)
        self.max_gauss = self.a_to_g(self.max_amp)
        self.step_gauss = self.a_to_g(self.step_amp)
    
    # Generating the Power Supply sequence for current sourcing
    def PS_curr_seq(self, start_curr, min_curr, max_curr, step_curr, loops):
        seq_start = np.arange(start_curr, max_curr, step_curr)
        seq_loop = np.concatenate((np.arange(max_curr, min_curr, -step_curr), np.arange(min_curr, max_curr, step_curr)))
        seq = []
        seq = np.concatenate((seq, seq_start))
        for i in range(loops):
            seq = np.concatenate((seq, seq_loop))
        return seq

    # Biasing field control
    def bias_y(self):
        if self.bias_ON == 1:
            self.PowerSupply_Y.enable_output()
            self.PowerSupply_Y.voltage = 50
            self.PowerSupply_Y.output_current_relay(self.g_to_a(self.bias_gauss))
        elif self.bias_ON == 0:
            self.PowerSupply_Y.disable_output()
        else:
            raise Exception(f"TransferCurve: Invalid biasing field(gauss) input: {str(e)}")
            
    # Sourcemeter params
    def SM_MTJ_curr(self):
        if self.square_wave == True:
            MTJ_curr_arr = np.repeat([self.MTJ_operating_curr, -self.MTJ_operating_curr],(self.cycle_length))
        elif self.square_wave == False:
            MTJ_curr_arr = np.repeat(self.MTJ_operating_curr, (self.cycle_length))
        else:
            raise Exception(f"TransferCurve: Invalid current sample input: {str(e)}")
        return MTJ_curr_arr
    
    '''
    Inheriting the execute function in procedure.
    In the graphic display, when the queue button is hit, this function will be executed.
    '''
    def execute(self):
        # unit conversion
        if self.gauss_or_amp == True:
            self.to_amp()
        elif self.gauss_or_amp == False:
            self.to_gauss()
        else: 
            raise Exception(f"TransferCurve: Invalid gauss or amp input: {str(e)}")
            
        # PowerSupply configs
        self.PowerSupply_X.enable_output()
        self.PowerSupply_X.output_voltage = abs(start_amp)*50
        
        # Biasing field
        self.bias_y()
        
        # Sequence of current sourcing
        curr_seq = self.PS_curr_seq(self.start_amp, self.min_amp, self.max_amp, self.step_amp, self.loop)
        
        # SourceMeter sourcing constant current for MTJ operation
        self.SourceMeter.enable_source()
        self.SourceMeter.apply_current(self.default_MTJ_operating_current_range, self.voltage_range) # default_MTJ_operating_current_range = 0.002, voltage_range = 6
        self.SourceMeter.measure_voltage(self.NPLC, self.voltage_range)                              # NPLC = 0.01, voltage_range = 6
        self.SourceMeter.source_curr_mode('LIST')                                                    # Setting the MTJ current for each discrete magnetic field to be a list of current values
        self.SourceMeter.source_list_current(self.SM_MTJ_curr())
        
        # Start time counting
        start = timeit.default_timer()
        
        # For loop 
        # Iterating the current sequence for the power supply
        for i, curr in enumerate(curr_seq):
            log.info("Setting the current to %g A" % curr)
            
            # Output current to the electromagnet (using the function with built-in relay)
            self.PowerSupply_X.output_current_relay(curr)
            
            # Averaging the measured voltages across the sample
            volt = np.average(np.absolute(self.SourceMeter.voltage))
            
            # Time tracking
            time = timeit.default_timer() - start
            
            # Resistance of the sample
            resistance = volt/self.MTJ_operating_curr
            
            print("t: ", time)
            print("v: ", volt)
            print("i: ", curr)
            print("r: ", resistance, "\n")
            
            # Render data in a tuple
            data = {
                'Time (s)': time,
                'Current (A)': curr,
                'Voltage (V)': volt,
                'Magnetic Field (G)': self.a_to_g(curr),
                'Resistance (V/A)': resistance
            }
            self.emit('results', data)
            self.emit('progress', 100. * i / len(curr_seq))
            if self.should_stop():
                log.info("User aborted the procedure")
                break
    
    '''
    Inheriting the shutdown function from the procedure class.
    Turn off the sourcemeter and the power supplies.
    '''
    def shutdown(self):
        self.SourceMeter.shutdown()
        self.PowerSupply_X.shutdown()
        self.PowerSupply_Y.shutdown()
        log.info("Finished measuring")

# The class for transfer curve window
class TransferCurveWindow(ManagedWindow):

    def __init__(self):
        super().__init__(
            procedure_class=TransferCurveProcedure,
            # Initialize all the required inputs
            inputs=['gauss_or_amp', 'start_gauss', 'min_gauss', 'max_gauss', 'step_gauss', 
            'start_amp', 'min_amp', 'max_amp', 'step_amp', 'loop', 'bias_ON', 'bias_gauss',
            'toggle', 'MTJ_operating_curr','cycle_length', 'square_wave', 'NPLC', 'voltage_range'],
            
            # Choose the inputs to be displayed
            displays=['gauss_or_amp', 'start_gauss', 'min_gauss', 'max_gauss', 'step_gauss', 
            'start_amp', 'min_amp', 'max_amp', 'step_amp', 'loop', 'bias_ON', 'bias_gauss',
            'toggle', 'MTJ_operating_curr','cycle_length', 'square_wave', 'NPLC', 'voltage_range'],
            
            x_axis='Magnetic Field (G)',
            y_axis='Resistance (V/A)'
        )
        self.setWindowTitle('Transfer Curve')
        
        #self.filename = r'IV'   # Sets default filename
        #self.directory = r"./"           # Sets default directory
        #self.store_measurement = True                              # Controls the 'Save data' toggle
        #self.file_input.extensions = ["csv", "txt", "data"]         # Sets recognized extensions, first entry is the default extension
        #self.file_input.filename_fixed = False                      # Controls whether the filename-field is frozen (but still displayed)
        
    def queue(self):
        directory = "./data/"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='TransferCurve')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)


if __name__ == "__main__":
    
    app = QtWidgets.QApplication(sys.argv)
    window = TransferCurveWindow()
    window.show()
    sys.exit(app.exec())