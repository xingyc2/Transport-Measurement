from pymeasure.instruments.keithley import Keithley2400
from pymeasure.log import console_log
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Procedure, Results, IntegerParameter, FloatParameter, Parameter, unique_filename
from time import sleep
import numpy as np
import sys
import tempfile

from pymeasure.log import log, console_log

class TransferCurveProcedure(Procedure):

    data_points = IntegerParameter('Data points', default=20)
    max_current = FloatParameter('Maximum Current', units='A', default=0.001)
    min_current = FloatParameter('Minimum Current', units='A', default=-0.001)

    #DATA_COLUMNS = ['Current (A)', 'Voltage (V)', 'Voltage Std (V)', 'Resistance (V/A)']
    DATA_COLUMNS = ['Current (A)', 'Voltage (V)', 'Resistance (V/A)']


    def startup(self):
        log.info("Connecting and configuring the instrument")
        self.sourcemeter = Keithley2400("GPIB::20")
        self.sourcemeter.reset()
        self.sourcemeter.use_front_terminals()
        self.sourcemeter.nplc = 0.01
        self.sourcemeter.apply_current(100e-3, 10.0)  # current_range = 100e-3, compliance_voltage = 10.0
        self.sourcemeter.measure_voltage(0.01, 1.0)  # nplc = 0.01, voltage_range = 1.0
        sleep(0.1)  # wait here to give the instrument time to react
        self.sourcemeter.stop_buffer()
        self.sourcemeter.disable_buffer()

    def execute(self):
        currents = np.linspace(
            self.min_current,
            self.max_current,
            num=self.data_points
        )
        self.sourcemeter.enable_source()
        # Loop through each current point, measure and record the voltage
        for i, current in enumerate(currents):
            log.info("Setting the current to %g A" % current)
            self.sourcemeter.source_current = current
            log.info("Waiting for the buffer to fill with measurements")

            data = {
                'Current (A)': current,
                'Voltage (V)': self.sourcemeter.voltage,
                'Resistance (V/A)': self.sourcemeter.voltage / current
            }
            self.emit('results', data)
            self.emit('progress', 100. * i / self.data_points)
            sleep(0.01)
            if self.should_stop():
                log.info("User aborted the procedure")
                break
                
    def get_estimates(self, sequence_length=None, sequence=None):

        return self.data_points * 0.05

    def shutdown(self):
        self.sourcemeter.shutdown()
        log.info("Finished measuring")
        
class IVWindow(ManagedWindow):

    def __init__(self):
        super().__init__(
            procedure_class=IVProcedure,
            inputs=['data_points', 'min_current', 'max_current'],
            displays=['data_points', 'min_current', 'max_current'],
            x_axis='Current (A)',
            y_axis='Voltage (V)'
        )
        self.setWindowTitle('IV Curve')
        
        #self.filename = r'IV'   # Sets default filename
        #self.directory = r"./"           # Sets default directory
        #self.store_measurement = True                              # Controls the 'Save data' toggle
        #self.file_input.extensions = ["csv", "txt", "data"]         # Sets recognized extensions, first entry is the default extension
        #self.file_input.filename_fixed = False                      # Controls whether the filename-field is frozen (but still displayed)
        
    def queue(self):
        directory = "./"  # Change this to the desired directory
        filename = unique_filename(directory, prefix='IV')

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)


if __name__ == "__main__":
    
    app = QtWidgets.QApplication(sys.argv)
    window = IVWindow()
    window.show()
    sys.exit(app.exec())