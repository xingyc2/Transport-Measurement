import numpy as np

def reporter(f,x): 
    try:
        if f(x):  
            # f(x) is not None and not throw any exception. Your last case
            return "Generic"
        # f(x) is `None`
        return "No Problem"
    except ValueError:
        return 'Value'
    except TypeError:
        return 'Type'
    except E2OddException:
        return 'E2Odd'


#print('x'(2))

class test():
    def __init__(self):
        pass

    def arr_to_str(self, a, 
                    pts, on):
        if type(on) == bool:
            if on == False:
                return np.repeat(a,(pts))
            else:
                return np.repeat([a, -a],(pts))
        else:
            print("Error")
            
def ii(a, b):
    return a, b

if __name__ == '__main__':
    #a = np.arange(0, 0.001, 0.00005)
    #a = np.append(a, 0.001)
    aa, bb = ii(1, 2)
    print(aa)
    print(bb)
    # Separate by delimiter
    # print(','.join([str(i) for i in arr]))