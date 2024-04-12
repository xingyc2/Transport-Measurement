import time
import zhinst.core
from zhinst.toolkit import Session
import matplotlib.pyplot as plt
import numpy as np

'''
device_id = "dev7173" # Device serial number available on its rear panel.
interface = "1GbE" # For Ethernet connection or when MFLI/MFIA is connected to a remote Data Server.

server_host = "localhost"
server_port = 8004
api_level = 1 # Maximum API level supported for all instruments except HF2LI.

# Create an API session to the Data Server.
daq = zhinst.core.ziDAQServer(server_host, server_port, api_level)
# Establish a connection between Data Server and Device.
daq.connectDevice(device_id, interface)
'''
session = Session('localhost')
device = session.connect_device('dev7173')

print(list(device.child_nodes()))
print(list(device.demods[0].child_nodes(recursive=True)))


device.demods[0].sample.subscribe()
time.sleep(1)
device.demods[0].sample.unsubscribe()
poll_result = session.poll()
demod_sample = poll_result[device.demods[0].sample]

print(demod_sample)
r = np.sqrt(np.square(demod_sample["x"]) + np.square(demod_sample["y"]))

_, axis = plt.subplots(1, 1)
axis.plot(r)
axis.grid(True)
axis.set_title("X Data from the polled demod sample")
axis.set_xlabel("Sample")
axis.set_ylabel("Value")
plt.show()