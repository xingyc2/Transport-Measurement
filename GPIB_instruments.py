import sys
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from device import MeasurementDevice
import time

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
            self.volt = 0
            self.curr = 0
            self.rel = 1
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
                self.rel = -1
            else:
                self.set_values("OUTP:REL ON")
                self.set_values("OUTP:REL:POL NORM")
                self.rel = 1
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
        self.volt = volt
        try:
            if volt <= 51 and volt >= 0:
                self.set_values("VOLT " + str(volt))
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
        self.curr = curr
        try:
            if curr < 0:
                self.relay(True)
            else:
                self.relay(False)
            curr = abs(curr)
            if curr <= 1.1 and curr >= 0 :
                self.set_values("CURR " + str(curr))
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
            
    def compliance_level(self):
        if (abs(self.curr) > 0.015) and (self.volt != 51):
            self.set_values("VOLT 51")
            self.volt = 51
            time.sleep(.3)
            #time.sleep(.1)
        elif (abs(self.curr) > 0.001) and (abs(self.curr) < 0.015) and (self.volt != 1):
            self.set_values("VOLT 1")
            self.volt = 1
            time.sleep(.3)
            #time.sleep(.1)
        elif (abs(self.curr) < 0.001) and (self.volt != 0.05):
            self.set_values("VOLT 0.1")
            self.volt = 0.05
            time.sleep(.3)
            #time.sleep(.1)
    
    def read_I(self, in_float=True):
        """
        Read the output current. 
        
        Raises:
        - Exception: If any issues with communication or data retrieval occur.
        """
        try:
            result = self.get_values("MEAS:CURR?")
            if in_float == True:
                return self.rel*float(result)
            else:
                return self.get_values("MEAS:CURR?")
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
        
        
    
class Agilent2400_SourceMeter(MeasurementDevice):
    def str_float(self, raw, sep=','):
        return [float(i) for i in raw.split(sep)]
        
    def source_func(self, func="CURR"):
        try:
            if func == "CURR":
                self.set_values("SOUR:FUNC CURR")
            elif func == "VOLT":
                self.set_values("SOUR:FUNC VOLT")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent2400_SourceMeter: Invalid source function input: {str(e)}")
    
    def sense_func(self, func="VOLT"):
        try:
            if func == "CURR":
                self.set_values("SENS:FUNC \"CURR\"")
            elif func == "VOLT":
                self.set_values("SENS:FUNC \"VOLT\"")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent2400_SourceMeter: Invalid sense function input: {str(e)}")
    
    def source_curr_mode(self, option="LIST"):
        try:
            if option == "FIXED":
                self.set_values("SOUR:CURR:MODE FIX")
            elif option == "LIST":
                self.set_values("SOUR:CURR:MODE LIST")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent2400_SourceMeter: Invalid source current mode input: {str(e)}")
    
    def source_curr_range(self, curr_range=0.001):
        try:
            self.set_values("SOUR:CURR:RANG " + str(curr_range))
            self.curr_range = curr_range
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent2400_SourceMeter: Invalid source current range input: {str(e)}")
    
    def sense_volt_range(self, volt_range=2):
        try:
            self.set_values("SENS:VOLT:RANG " + str(volt_range))
            self.volt_range = volt_range
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent2400_SourceMeter: Invalid sense voltage range input: {str(e)}")
      
    def form_element(self, option="VOLT"):
        try:
            self.set_values("FORM:ELEM " + option)
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent2400_SourceMeter: Invalid form input: {str(e)}")
    
    def initialize(self, scfunc="CURR", ssfunc="VOLT", scmode="LIST", scrange=0.001, svrange=10, fe="VOLT"):
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
            self.source_func(scfunc)
            self.sense_func(ssfunc)
            self.source_curr_mode(scmode)
            self.source_curr_range(scrange)
            self.sense_volt_range(svrange)
            self.form_element(fe)
        except:
            print(self.get_values("SYST:ERR?"))
    
    def NPLC(self, nplc=0.03):
        try:
            self.set_values("NPLC " + str(nplc))
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent2400_SourceMeter: Invalid NPLC input: {str(e)}")
        
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
            raise Exception(f"Agilent2400_SourceMeter: Invalid output input: {str(e)}")
        
        
    def trigger_count(self, counts):
        """
        Turn on/off the relay switch, which alters the direction of the current.
        
        Parameter:
        - relay (boolean): Relay on/off, when it is on, negative current will be sourced;
                           otherwise, positive current will be sourced. (Default to be off)
        
        Raises
        - Exception: Invalid input of relay parameter or communication issue.
        """
        try:
            self.set_values("TRIG:COUN " + str(counts))
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent2400_SourceMeter: Invalid trigger count input: {str(e)}")
        
    def source_V(self, volt=0):
        """
        Set the output voltage.
        
        Parameters:
        - volt(float): Value of voltage(V). (Default to be 0)
        
        Raises:
        - Exception: Invalid input of voltage parameter or communication issue.
        """
        try:
            if volt <= self.volt_range and volt >= 0:
                self.set_values("VOLT " + str(volt))
            else:
                print(f"Agilent2400_SourceMeter: Voltage input exceeds sourcing voltage range.")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent2400_SourceMeter: Invalid voltage input(value must : {str(e)}")
    
    def source_I(self, curr=0):
        """
        Set the output current(compliance). 
        
        Parameters:
        - curr(float): Value of current(A). (Default to be 0)
        
        Raises:
        - Exception: Invalid input of current parameter or communication issue.
        """
        try:
            if curr <= self.curr_range and curr >= 0:
                self.set_values("SOUR:CURR " + str(curr))
            else:
                print(f"Agilent2400_SourceMeter: Current input exceeds sourcing current range.")
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent2400_SourceMeter: Invalid current input: {str(e)}")
    
    def curr_list(self, curr, pts):
        curr_input = ''
        curr_input += str(curr)
        for i in range(pts-1):
            curr_input += ','+str(curr)
        return curr_input
    
    def source_list_I(self, curr):
        """
        Set a list of output current values. 
        
        Parameters:
        - curr(str/list): A list of values of current(A).
        
        Raises:
        - Exception: Invalid input of current parameter or communication issue.
        """
        try:
            if type(curr) == str:
                self.set_values("SOUR:LIST:CURR " + curr)
                self.trigger_count(len(self.str_float(curr)))
            else:
                c = ','.join([str(i) for i in curr])
                self.set_values("SOUR:LIST:CURR " + c)
                self.trigger_count(len(curr))
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent2400_SourceMeter: Invalid current input, must be either a string of values or a list of values{str(e)}")
    
    '''
    def source_list_I(self, *curr, pts):
        """
        Set a list of output current values. 
        
        Parameters:
        - curr(str): A list of values of current(A).
        - pts(int): The multiple of the value(s) in curr to be repeated
        
        Raises:
        - Exception: Invalid input of current parameter or communication issue.
        """
        try:
            if type(curr) == str:
                self.set_values("SOUR:LIST:CURR " + self.curr_list(curr, pts))
            elif type(curr) == float:
                try:
                    if curr <= 1 and curr >= 0:
                        self.set_values("SOUR:LIST:CURR " + self.curr_list(curr, pts))
                except:
                    print(f"Agilent2400_SourceMeter: Voltage input exceeds sourcing voltage range.")
            elif type(curr) == list:
                self.set_values("SOUR:LIST:CURR " + str(curr*pts))[1:-1]
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent2400_SourceMeter: Invalid current input: {str(e)}")
    '''
    
    
    def read_buffer(self):
        """
        Read the output current. 
        
        Raises:
        - Exception: If any issues with communication or data retrieval occur.
        """
        try:
            return self.str_float(self.get_values("READ?"))
        except Exception as e:
            print(self.get_values("SYST:ERR?"))
            raise Exception(f"Agilent2400_SourceMeter: Failed to read buffer: {str(e)}")
            
            
if __name__ == "__main__":
    try:
        ps1 = Agilent6613C_PowerSupply('GPIB0::5::INSTR' )
        ps2 = Agilent6613C_PowerSupply('GPIB0::9::INSTR' )
        sm = Agilent2400_SourceMeter('GPIB0::20::INSTR' )
    
    except Exception as e:
        print(f"Error: {str(e)}")