import os
import pyvisa
import time
import timeit
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#import Instr_lib as instrlib
import device
from GPIB_instruments import Agilent6613C_PowerSupply, Agilent2400_SourceMeter

Agilent6613C_PowerSupply('GPIB0::5::INSTR')
Agilent6613C_PowerSupply('GPIB0::9::INSTR')
Agilent2400_SourceMeter('GPIB0::20::INSTR')