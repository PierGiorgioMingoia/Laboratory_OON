import numpy as np
import json
import matplotlib.pyplot as plt
import math


class Signal_information:
    def __init__(self, signal_power, path):
        self.signal_power = signal_power
        self.noise_power = 0
        self.latency = 0
        self.path = path

    def update_signal_power(self, increment):
        self.signal_power += increment

    def update_noise_power(self, increment):
        self.noise_power += increment

    def update_latency(self, increment):
        self.latency += increment

    def update_path(self):
        self.path.pop(0)


class Node:
    def __init__(self, d):
        for key, value in d.items():
            setattr(self, key, value)
        self.successive = dict()

    def propagate(self, signal_information):
        signal_information.update_path()
        self.successive.propagate(signal_information)


class Line:
    def __init__(self, label, length):
        self.label = label
        self.length = length
        self.successive = {}

    def latency_generation(self, signal_information):
        speed_of_light = 299792458  # m/s
        lat = self.length / speed_of_light
        signal_information.update_latency(lat)

    def noise_generation(self, signal_information):
        noise = 1 ** (np.exp(1) * signal_information.signal_power * self.length)
        signal_information.update_noise_power(noise)


class Network:
    def __init__(self, json_file):
        self.nodes = dict()
        self.lines = dict()
        with open(json_file) as f:
            network_data = json.load(f)
        for key, value in network_data.items():
            n = Node({"label": key, **value})
            self.nodes[key] = n
            pos = value['position']
            for n in value['connected_nodes']:
                label = key + n
                next_pos = network_data[n]['position']
                length = distance_nodes(pos, next_pos)
                line = Line(label, length)
                self.lines[label] = line

    def connect(self):
        for key in self.nodes:
            for k in self.lines:
                if k.startswith(key):
                    self.nodes[key].successive[k] = self.lines[k]
        print(self.nodes['A'].successive)
        for key in self.lines:
            for k in self.nodes:
                if key.endswith(k):
                    self.lines[key].successive[k] = self.nodes[k]
        print(self.lines['DA'].successive['A'].successive)


    def find_paths(self, node1, node2):
        pass

    def propagate(self):
        pass


def distance_nodes(x, y):
    return np.linalg.norm(np.array(x) - np.array(y))


if __name__ == '__main__':
    net = Network('./data/nodes.json')
    net.connect()
