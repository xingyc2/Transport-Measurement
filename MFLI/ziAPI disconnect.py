import pyvisa
import time
import timeit
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import zhinst.core

# MFLI by Zurich Instrument config
device_id = "dev7173" # Device serial number available on its rear panel.
interface = "1GbE" # For Ethernet connection or when MFLI/MFIA is connected to a remote Data Server.
#interface = "PCIe" # For MFLI/MFIA devices in case the Data Server runs on the device.
server_host = "localhost"
server_port = 8004
api_level = 6 # 

daq = zhinst.core.ziDAQServer(server_host, server_port, api_level)
daq.disconnectDevice(device_id)