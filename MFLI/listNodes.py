import pyvisa
import time
import timeit
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import zhinst.core
import pickle
import csv

rm = pyvisa.ResourceManager()
print(rm.list_resources())

device_id = "dev7173" # Device serial number available on its rear panel.
interface = "1GbE" # For Ethernet connection or when MFLI/MFIA is connected to a remote Data Server.
server_host = "localhost"
server_port = 8004
api_level = 1 # Maximum API level supported for all instruments except HF2LI.
# Create an API session to the Data Server.
daq = zhinst.core.ziDAQServer(server_host, server_port, api_level)
# Establish a connection between Data Server and Device.
daq.connectDevice(device_id, interface)
daq_module = daq.dataAcquisitionModule()


'''
Get attributes from the MFLI server.
'''
print(daq.__dir__())

'''
Get all the nodes from the MFLI server.
'''
print(daq.listNodes('/dev7173'))

daq.set('/dev7173/features/code', 0)