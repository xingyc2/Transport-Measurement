import sys
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from device import MeasurementDevice

class Agilent6613C(MeasurementDevice):
    def initialize(self):
        super().connect()
        self.instument.write("*RST")
        self.instument.write("*CLS")
        self.instument.write("SENSe:SWEep:POINts 256")
        
    def relay(self, rel):
        if rel == True:
            self.instrument.write("OUTP:REL ON")
            self.instrument.write("OUTP:REL:POL REV")
        else:
            self.instrument.write("OUTP:REL ON")
            self.instrument.write("OUTP:REL:POL NORM")
        
    def source_volt(self, volt):
        self.instument.write("VOLT " + volt)
        
    def source_volt(self, volt):
        self.instument.write("VOLT " + volt)
        
    def source_curr(self, curr):
        self.instument.write("CURR " + curr)
        
    def source_curr(self, curr, volt):
        self.instument.write("CURR " + curr + ";VOLT " + volt)
        
    
        