import sys
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from device import MeasurementDevice

class Agilent6613C(MeasurementDevice):
    def __init__(self, visa_address):
        self.visa_address = visa_address
        
        MeasurementDevice.__init__(self, visa_address)
        MeasurementDevice.connect(self)