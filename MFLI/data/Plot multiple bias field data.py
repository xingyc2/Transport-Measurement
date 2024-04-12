import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Transfer curve

data_95 = pd.read_excel("95.xlsx", dtype={'HHC field amplitude(G)': float, 'Sensitivity(%/G)': float})
print(data_95)
data_195 = pd.read_excel("195.xlsx")
#data_363 = pd.read_excel("363.xlsx")
#data_743 = pd.read_excel("743.xlsx")

data_1503 = pd.read_excel("1503.xlsx")




fig, ax = plt.subplots()
ax.plot(data_95['HHC field amplitude(G)'], data_95['Sensitivity(%/G)'], color='b')
ax.plot(data_195['HHC field amplitude(G)'], data_195['Sensitivity(%/G)'], color='g')
#ax.plot(data_363['HHC field amplitude(G)'], data_363['Sensitivity(%/G)'], color='r')
#ax.plot(data_743['HHC field amplitude(G)'], data_743['Sensitivity(%/G)'], color='y')
ax.plot(data_1503['HHC field amplitude(G)'], data_1503['Sensitivity(%/G)'], color='r')
ax.set(xlabel='Magnetic field (G)', ylabel='Sensitivity(%/Oe)',
       title='Sensitivity measurement')
#ax.set_xlim(left=-.3, right=.3)
#ax.set_ylim(bottom=1950, top=5100)
ax.legend(['Frequency = 95 Hz', 'Frequency = 195 Hz', 'Frequency = 1503 Hz'], fontsize="12")
ax.grid()
ax.set_xscale('log')
ax.set_yscale('log')
plt.show()

