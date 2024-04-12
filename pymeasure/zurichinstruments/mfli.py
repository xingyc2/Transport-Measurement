#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging
import time

import numpy as np

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
#from pymeasure.instruments import Instrument, RangeException
#from pymeasure.instruments.validators import truncated_range, strict_discrete_set
import zhinst.core

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class MFLI(Instrument):
    device_id = "dev7173" # Device serial number available on its rear panel.
    interface = "1GbE" # For Ethernet connection or when MFLI/MFIA is connected to a remote Data Server.

    server_host = "localhost"
    server_port = 8004
    api_level = 1 # Maximum API level supported for all instruments except HF2LI.

    lowpass_order = 3
    demod_path = f"/{device_id}/demods/0/sample"

    total_duration = 1 # Time in seconds for the aquisition.
    module_sampling_rate = 10000  # Number of points/second.
    burst_duration = 0.2  # Time in seconds for each data burst/segment.
    num_cols = int(np.ceil(module_sampling_rate * burst_duration))
    num_bursts = int(np.ceil(total_duration / burst_duration))
    
    
    def __init__(self):
        # Create an API session to the Data Server.
        self.daq = zhinst.core.ziDAQServer(self.server_host, self.server_port, self.api_level)
        # Establish a connection between Data Server and Device.
        self.daq.connectDevice(self.device_id, self.interface)
        
        self.daq_module = self.daq.dataAcquisitionModule()

        self.daq_module.set("device", self.device_id)

    def enable_external_reference(self):
        self.daq.set(f"/{self.device_id}/extrefs/0/enable", 1)
        
    def disable_external_reference(self):
        self.daq.set(f"/{self.device_id}/extrefs/0/enable", 0)
        
    def enable_demodulator(self, demod=0):
        self.daq.setInt(f'/{self.device_id}/demods/' + demod + '/enable', 1)
        
    def disable_demodulator(self, demod=0):
        self.daq.setInt(f'/{self.device_id}/demods/' + demod + '/enable', 0)
    
#####   
    def enable_ac_coupling(self):
        self.daq.set(f"/{self.device_id}/sigins/0/ac", 1)
        
    def disable_ac_coupling(self):
        self.daq.set(f"/{self.device_id}/sigins/0/ac", 0)
        
    def enable_autorange(self):
        self.daq.set(f"/{self.device_id}/sigins/0/autorange", 1)
        
    def disable_autorange(self):
        self.daq.set(f"/{self.device_id}/sigins/0/autorange", 0)
        
    def enable_sinc(self):
        self.daq.set(f"/{self.device_id}/demods/0/sinc", 1)
        
    def disable_sinc(self):
        self.daq.set(f"/{self.device_id}/demods/0/sinc", 0)
        
        
        
    def test(self):
        self.enable_autorange()
        self.enable_sinc()
        self.daq.setDouble('/dev7173/demods/0/rate', 10e3)
        self.daq.subscribe('/dev7173/demods/0/sample')
        self.enable_ac_coupling()
        data = self.daq.poll(0.020, 10, 0, True)
        #print(data)
        time.sleep(0.2)
        return data
        
        
if __name__ == "__main__":
    try:
        LockIn = MFLI()
        LockIn.enable_external_reference()
        data = LockIn.test()['/dev7173/demods/0/sample']
        print(data)
        print(np.sqrt(np.average(data['x'])**2 + np.average(data['y'])**2))
    except Exception as e:
        print(f"Error: {str(e)}")
        