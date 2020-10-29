import numpy as np
import json
import matplotlib.pyplot as plt
import math
import itertools
import pandas as pd


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
        # TODO check if destination
        if len(signal_information.path) == 1:
            print("END OF PROPAGATION")
        else:
            # find the next line
            line_key = False
            for key in self.successive:
                if key.endswith(signal_information.path[1]):
                    line_key = key
            if line_key:
                next_line = self.successive[line_key]
                signal_information.update_path()
                next_line.propagate(signal_information)
            else:
                print('Invalid Path')


class Line:
    def __init__(self, label, length):
        self.label = label
        self.length = length
        self.successive = dict()

    def latency_generation(self):
        speed_of_light = 299792458  # m/s
        lat = self.length / speed_of_light
        return lat

    def noise_generation(self, signal_power):
        print(self.length)
        noise = 1e-3 * signal_power * self.length
        return noise

    def propagate(self, signal_information):
        lat_update = self.latency_generation()
        noise_update = self.noise_generation(signal_information.signal_power)
        signal_information.update_noise_power(noise_update)
        signal_information.update_latency(lat_update)
        self.successive[signal_information.path[0]].propagate(signal_information)


class Network:
    def __init__(self, json_file):
        self.nodes = dict()
        self.lines = dict()
        with open(json_file) as f:
            network_data = json.load(f)
        for key, value in network_data.items():
            node = Node({"label": key, **value})
            self.nodes[key] = node
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
        for key in self.lines:
            for k in self.nodes:
                if key.endswith(k):
                    self.lines[key].successive[k] = self.nodes[k]

    def find_paths(self, node1, node2):
        visited = {}
        for key in self.nodes:
            visited[key] = False
        paths = []
        path = []
        self.count_path_util(node1, node2, visited, path, paths)
        return paths

    def count_path_util(self, u, d, visited, path, paths):
        visited[u] = True
        path.append(u)

        if u == d:
            paths.append(path[:])
        else:
            for k in self.nodes[u].successive:
                if not visited[k[1]]:
                    self.count_path_util(k[1], d, visited, path, paths)
        path.pop()
        visited[u] = False

    def propagate(self, signal_information):
        self.nodes[signal_information.path[0]].propagate(signal_information)

    def draw(self):
        x = []
        y = []
        for key in self.lines:
            # print(key)
            x_values = [self.nodes[key[0]].position[0], self.nodes[key[1]].position[0]]
            y_values = [self.nodes[key[0]].position[1], self.nodes[key[1]].position[1]]
            plt.plot(x_values, y_values, linestyle='--', color='r')
        for key in self.nodes:
            # print(key)
            x.append(self.nodes[key].position[0])
            y.append(self.nodes[key].position[1])
        plt.plot(x, y, marker='o', color='b', linestyle='')
        plt.show()


def distance_nodes(x, y):
    return np.linalg.norm(np.array(x) - np.array(y))


def signal_to_noise_ratio(signal_power, noise):
    # Db = 10log10(w/w)
    return 10 * math.log10(signal_power / noise)


def all_possible_pairs(nodes):
    return list(itertools.combinations(nodes, 2))


if __name__ == '__main__':
    net = Network('./data/nodes.json')
    net.connect()
    net.find_paths('A', 'B')
    # net.draw()

    signal = Signal_information(0.001, ['B', 'A'])
    net.propagate(signal)
    print("Power of the signal: {}".format(signal.signal_power))
    print("Latency of the signal: {}".format(signal.latency))
    print("Noise of the signal: {}".format(signal.noise_power))
    print("Path of the signal: {}".format(signal.path))

    possible_pairs = all_possible_pairs(['A', 'B', 'C', 'D', 'E', 'F'])
    list_of_paths = []
    for pair in possible_pairs:
        pair_paths = net.find_paths(pair[0], pair[1])
        list_of_paths.append(pair_paths)
    # print(list_of_paths)

    all_signal_power = []
    all_signal_latency = []
    all_signal_noise = []
    all_signal_ratio = []
    all_path = []
    for paths in list_of_paths:
        for path in paths:
            print(path)
            signal = Signal_information(0.001, path)
            string_path = ''
            for node in path:
                string_path += node + '->'
            string_path = string_path[:-2]
            all_path.append(string_path)
            net.propagate(signal)
            all_signal_power.append(signal.signal_power)
            all_signal_latency.append(signal.latency)
            all_signal_noise.append(signal.noise_power)
            all_signal_ratio.append(signal_to_noise_ratio(signal.signal_power, signal.noise_power))

    print(len(all_path))
    print(len(all_signal_latency))

    df = pd.DataFrame({
        "Path": all_path,
        "Total_latency": all_signal_latency,
        "Total_noise": all_signal_noise,
        "Signal_noise_ratio": all_signal_ratio
    })

    print(df.head(5))
