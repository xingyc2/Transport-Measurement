import requests
import pyvisa
import timeit
import numpy as np
import pandas as pd
import Instr_lib as instrlib


rm = pyvisa.ResourceManager()
print(rm.list_resources())

# Agilent 6613C initalization
addr5 = rm.open_resource('GPIB0::5::INSTR')
addr9 = rm.open_resource('GPIB0::9::INSTR')
addr10 = rm.open_resource('GPIB0::10::INSTR')
addr19 = rm.open_resource('GPIB0::19::INSTR')
addr20 = rm.open_resource('GPIB0::20::INSTR')
#addr9.write("ABOR")
addr5.write("*RST")
addr5.write("*RST")
addr20.write("*CLS")


addr20.write(":OUTP OFF")
addr9.write("OUTP 0")
addr5.write("OUTP 0")
addr19.write("APPL:DC DEF, DEF, 0V")

error5 = addr5.query("SYST:ERR?")
print(error5)
error9 = addr9.query("SYST:ERR?")
print(error9)


error19 = addr19.query("SYST:ERR?")
print(error19)
error20 = addr20.query(":STAT:QUE?")
print(error20)
