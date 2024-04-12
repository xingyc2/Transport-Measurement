import pyvisa
import time
import timeit
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import zhinst.core

for i in zhinst.core.ziDAQServer.__dict__:
    print(i)