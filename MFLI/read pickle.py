import numpy as np
import time
import zhinst.core
import matplotlib.pyplot as plt
import pickle
'''
with open('MTJ_signal.pkl', 'rb') as fp:
    read_data = pickle.load(fp)
   
for k, v in read_data.items():
    print(k, v)
    
print(read_data)
r = read_data['/dev7173/demods/0/sample.r'][0]
print(r['value'])
freq = read_data['/dev7173/demods/0/sample.frequency'][0]
print(r['timestamp'][0])

keys = ['timestamp', 'value']
def extracttv(data, keys):
    data = {
            keys[0]: data[keys[0]][0] - data[keys[0]][0][0],
            keys[1]: data[keys[1]][0]
            }
    return data
r = extracttv(r, keys)
freq = extracttv(freq, keys)
data = {'r': r, 'frequency': freq}
print(data)


fig, ax = plt.subplots()
ax.scatter(data['r']['timestamp'], data['r']['value'])
plt.show()
'''
print(np.arange(10, 0, -1))