class MeasurementDevice:
    def __init__(self, value):
        self.value = value

    def a(self):
        self.value = self.value * 2
        
    def b(self):
        self.a()
        self.value = self.value + 1

    def curr_list(self, curr, pts):
        curr_input = ''
        curr_input += str(curr)
        for i in range(pts-1):
            curr_input += ','+str(curr)
        return curr_input

class Agilent6613C_PowerSupply(MeasurementDevice):
    def initialize(self):
        print('aaa')
        



if __name__ == "__main__": 
    device = Agilent6613C_PowerSupply(10)
    device.a()
    device.initialize()
    try:
        print(device.value)
    except:
        print(f"Error")