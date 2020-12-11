from classes import *
from classes.SignalInformation import Lightpath

if __name__ == '__main__':
    test_line = Line('AB', 380 * 1000)
    print(test_line.ase_generation())
    test_light_path = Lightpath(signal_power=0.001, path=['A', 'B'], channel=0)
    print(test_line.nli_generation(test_light_path))
