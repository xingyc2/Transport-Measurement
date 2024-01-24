import sys
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from device import MeasurementDevice

class Agilent6613C_PowerSupply(MeasurementDevice):
    def initialize(self):
        """
        Initialize the power supply with essential configs,
        including connection via pyvisa.
        
        Raises:
        - Exception: System error.
        """
        try:
            super().connect()
            self.set_values("*RST")
            self.set_values("*CLS")
            self.set_values("SENSe:SWEep:POINts 256")
        except:
            print(self.get_values("SYST:ERR?"))
            
    def output(self, output=False):
        """
        Turn on/off the output of the power supply.
        
        Parameter:
        - output (boolean): Output on/off. (Default to be off)
        
        Raises
        - Exception: Invalid input of output parameter or communication issue.
        """
        try:
            if output == True:
                self.set_values("OUTP 1")
            else:
                self.set_values("OUTP 0")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid output input: {str(e)}")
        
        
    def relay(self, rel=False):
        """
        Turn on/off the relay switch, which alters the direction of the current.
        
        Parameter:
        - relay (boolean): Relay on/off, when it is on, negative current will be sourced;
                           otherwise, positive current will be sourced. (Default to be off)
        
        Raises
        - Exception: Invalid input of relay parameter or communication issue.
        """
        try:
            if rel == True:
                self.set_values("OUTP:REL ON")
                self.set_values("OUTP:REL:POL REV")
            else:
                self.set_values("OUTP:REL ON")
                self.set_values("OUTP:REL:POL NORM")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid relay input: {str(e)}")
        
    def source_V(self, volt=0):
        """
        Set the output voltage(compliance).
        
        Parameters:
        - volt(float): Value of voltage(V). (Default to be 0)
        
        Raises:
        - Exception: Invalid input of voltage parameter or communication issue.
        """
        try:
            if volt < 51 and volt >= 0:
                self.set_values("VOLT " + volt)
            else:
                print(f"Agilent6613C_PowerSupply: Output voltage exceeds limitation.")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid voltage input(value must : {str(e)}")
        
    def source_I(self, curr=0):
        """
        Set the output current(compliance). 
        
        Parameters:
        - curr(float): Value of current(A). (Default to be 0)
        
        Raises:
        - Exception: Invalid input of current parameter or communication issue.
        """
        try:
            if curr < 0:
                self.relay(True)
            else:
                self.relay(False)
            curr = abs(curr)
            if curr <= 1.1 and curr >= 0 :
                self.set_values("CURR " + curr)
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid current input: {str(e)}")
        
    def source_VI(self, volt=0, curr=0):
        """
        Set the output voltage and current. 
        
        Parameters:
        - volt(float): Value of voltage(V). (Default to be 0)
        - curr(float): Value of current(A). (Default to be 0)
        
        Raises:
        - Exception: Invalid input of voltage or current parameter or communication issue.
        """
        try:
            self.source_volt(volt)
            self.source_curr(curr)
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid voltage or current input: {str(e)}")
            
    def read_I(self):
        """
        Read the output current. 
        
        Raises:
        - Exception: If any issues with communication or data retrieval occur.
        """
        try:
            self.get_values("MEAS:CURR?")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Failed to read current from the Agilent6613C_PowerSupply: {str(e)}")
            
    def read_V(self):
        """
        Read the output voltage. 
        
        Raises:
        - Exception: If any issues with communication or data retrieval occur.
        """
        try:
            self.get_values("MEAS:VOLT?")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Failed to read voltage from the Agilent6613C_PowerSupply: {str(e)}")
        
        
    
class Agilent2400SourceMeter(MeasurementDevice):
    def source_func(self, func="CURR"):
        try:
            if func == "CURR":
                self.set_values("SOUR:FUNC CURR")
            else if == "VOLT":
                self.set_values("SOUR:FUNC VOLT")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid source function input: {str(e)}")
    
    def sense_func(self, func="VOLT"):
        try:
            if func == "CURR":
                self.set_values("SENS:FUNC \"CURR\"")
            else if == "VOLT":
                self.set_values("SENS:FUNC \"VOLT\"")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid sense function input: {str(e)}")
    
    def source_curr_mode(self, option="LIST"):
        try:
            if func == "FIXED":
                self.set_values("SOUR:CURR:MODE FIX")
            else if == "LIST":
                self.set_values("SOUR:CURR:MODE LIST")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid source current mode input: {str(e)}")
    
    def source_curr_range(self, curr_range=0.001):
        try:
            self.set_values("SOUR:CURR:RANG " + curr_range)
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid source current range input: {str(e)}")
    
    def sense_volt_range(self, volt_range=10):
        try:
            self.set_values("SENS:VOLT:RANG " + volt_range)
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid sense voltage range input: {str(e)}")
      
    def form_element(self, option="VOLT"):
        try:
            self.set_values("FORM:ELEM " + option)
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid form input: {str(e)}")
    
    def form_element(self, option="VOLT"):
        try:
            self.set_values("FORM:ELEM " + option)
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid form input: {str(e)}")
    
    def nplc(self, nplc):
        try:
            self.set_values("NPLC " + nplc)
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid NPLC input: {str(e)}")
        
    def initialize(self):
        """
        Initialize the source meter with essential configs,
        including connection via pyvisa, sourcing function, sensing function, 
        sourcing mode, sourcing range, sensing range, sensing value format.
        
        Raises:
        - Exception: System error.
        """
        try:
            super().connect()
            self.set_values("*RST")
            self.set_values("*CLS")
            self.source_func()
            self.sense_func()
            self.source_curr_mode()
            self.source_curr_range()
            self.sense_volt_range()
            self.form_element()
        except:
            print(self.get_values("SYST:ERR?"))
            
    def output(self, output=False):
        """
        Turn on/off the output of the power supply.
        
        Parameter:
        - output (boolean): Output on/off. (Default to be off)
        
        Raises
        - Exception: Invalid input of output parameter or communication issue.
        """
        try:
            if output == True:
                self.set_values("OUTP 1")
            else:
                self.set_values("OUTP 0")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid output input: {str(e)}")
        
        
    def relay(self, rel=False):
        """
        Turn on/off the relay switch, which alters the direction of the current.
        
        Parameter:
        - relay (boolean): Relay on/off, when it is on, negative current will be sourced;
                           otherwise, positive current will be sourced. (Default to be off)
        
        Raises
        - Exception: Invalid input of relay parameter or communication issue.
        """
        try:
            if rel == True:
                self.set_values("OUTP:REL ON")
                self.set_values("OUTP:REL:POL REV")
            else:
                self.set_values("OUTP:REL ON")
                self.set_values("OUTP:REL:POL NORM")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid relay input: {str(e)}")
        
    def source_V(self, volt=0):
        """
        Set the output voltage(compliance).
        
        Parameters:
        - volt(float): Value of voltage(V). (Default to be 0)
        
        Raises:
        - Exception: Invalid input of voltage parameter or communication issue.
        """
        try:
            if volt < 51 and volt >= 0:
                self.set_values("VOLT " + volt)
            else:
                print(f"Agilent6613C_PowerSupply: Output voltage exceeds limitation.")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid voltage input(value must : {str(e)}")
        
    def source_I(self, curr=0):
        """
        Set the output current(compliance). 
        
        Parameters:
        - curr(float): Value of current(A). (Default to be 0)
        
        Raises:
        - Exception: Invalid input of current parameter or communication issue.
        """
        try:
            if curr < 0:
                self.relay(True)
            else:
                self.relay(False)
            curr = abs(curr)
            if curr <= 1.1 and curr >= 0 :
                self.set_values("CURR " + curr)
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid current input: {str(e)}")
        
    def source_VI(self, volt=0, curr=0):
        """
        Set the output voltage and current. 
        
        Parameters:
        - volt(float): Value of voltage(V). (Default to be 0)
        - curr(float): Value of current(A). (Default to be 0)
        
        Raises:
        - Exception: Invalid input of voltage or current parameter or communication issue.
        """
        try:
            self.source_volt(volt)
            self.source_curr(curr)
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent6613C_PowerSupply: Invalid voltage or current input: {str(e)}")
            
    def read_I(self):
        """
        Read the output current. 
        
        Raises:
        - Exception: If any issues with communication or data retrieval occur.
        """
        try:
            self.get_values("MEAS:CURR?")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Failed to read current from the Agilent6613C_PowerSupply: {str(e)}")
            
    def read_V(self):
        """
        Read the output voltage. 
        
        Raises:
        - Exception: If any issues with communication or data retrieval occur.
        """
        try:
            self.get_values("MEAS:VOLT?")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Failed to read voltage from the Agilent6613C_PowerSupply: {str(e)}")