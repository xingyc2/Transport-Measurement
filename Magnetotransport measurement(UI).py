import os
import pyvisa
import time
import timeit
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import Instr_lib as instrlib

rm = pyvisa.ResourceManager()
print(rm.list_resources())

# Initialize instrument object using pyvisa
addr5 = rm.open_resource('GPIB0::5::INSTR')
addr9 = rm.open_resource('GPIB0::9::INSTR')
addr20 = rm.open_resource('GPIB0::20::INSTR')

class transferCurve