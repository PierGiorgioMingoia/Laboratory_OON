import numpy as np
import json
import matplotlib.pyplot as plt
import math
import itertools
import pandas as pd


class Signal_information:
    def __init__(self, signal_power, path, latency=None, noise_power=None):
        self._signal_power = signal_power
        if noise_power:
            self._noise_power = noise_power
        else:
            self._noise_power = 0
        if latency:
            self._latency = latency
        else:
            self._latency = 0
        self._path = path

    @property
    def signal_power(self):
        return self._signal_power

    @property
    def noise_power(self):
        return self._noise_power

    @property
    def latency(self):
        return self._latency

    @property
    def path(self):
        return self._path

    def update_signal_power(self, increment):
        self._signal_power += increment

    def update_noise_power(self, increment):
        self._noise_power += increment

    def update_latency(self, increment):
        self._latency += increment

    def update_path(self):
        self._path.pop(0)


class Node:
    def __init__(self, d):
        for key, value in d.items():
            setattr(self, key, value)
        self._successive = dict()

    @property
    def successive(self):
        return self._successive

    def propagate(self, signal_information):
        if len(signal_information.path) == 1:
            print("END OF PROPAGATION")
        else:
            # find the next line
            line_key = False
            for key in self._successive:
                if key.endswith(signal_information.path[1]):
                    line_key = key
            if line_key:
                next_line = self._successive[line_key]
                signal_information.update_path()
                next_line.propagate(signal_information)
            else:
                print('Invalid Path')


class Line:
    def __init__(self, label, length):
        self._label = label
        self._length = length
        self._successive = dict()

    @property
    def label(self):
        return self._label

    @property
    def length(self):
        return self._label

    @property
    def successive(self):
        return self._successive

    def latency_generation(self):
        speed_of_light = 299792458 * 2 / 3  # m/s
        lat = self._length / speed_of_light
        return lat

    def noise_generation(self, signal_power):
        noise = 1e-3 * signal_power * self._length
        return noise

    def propagate(self, signal_information):
        lat_update = self.latency_generation()
        noise_update = self.noise_generation(signal_information.signal_power)
        signal_information.update_noise_power(noise_update)
        signal_information.update_latency(lat_update)
        self.successive[signal_information.path[0]].propagate(signal_information)


class Network:
    def __init__(self, json_file):
        self._nodes = dict()
        self._lines = dict()
        with open(json_file) as f:
            network_data = json.load(f)
        for key, value in network_data.items():
            node = Node({"label": key, **value})
            self._nodes[key] = node
            pos = value['position']
            for n in value['connected_nodes']:
                label = key + n
                next_pos = network_data[n]['position']
                length = distance_nodes(pos, next_pos)
                line = Line(label, length)
                self._lines[label] = line

    @property
    def nodes(self):
        return self._nodes

    @property
    def lines(self):
        return self._lines

    def connect(self):
        for key in self._nodes:
            for k in self._lines:
                if k.startswith(key):
                    self._nodes[key].successive[k] = self._lines[k]
        for key in self._lines:
            for k in self._nodes:
                if key.endswith(k):
                    self._lines[key].successive[k] = self._nodes[k]

    def find_paths(self, node1, node2):
        visited = {}
        for key in self._nodes:
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
            for k in self._nodes[u].successive:
                if not visited[k[1]]:
                    self.count_path_util(k[1], d, visited, path, paths)
        path.pop()
        visited[u] = False

    def propagate(self, signal_information):
        self._nodes[signal_information.path[0]].propagate(signal_information)

    def draw(self):
        x = []
        y = []
        for key in self._lines:
            # print(key)
            x_values = [self._nodes[key[0]].position[0], self._nodes[key[1]].position[0]]
            y_values = [self._nodes[key[0]].position[1], self._nodes[key[1]].position[1]]
            plt.plot(x_values, y_values, linestyle='--', color='r')
        for key in self._nodes:
            # print(key)
            x.append(self._nodes[key].position[0])
            y.append(self._nodes[key].position[1])
        plt.plot(x, y, marker='o', color='b', linestyle='')
        plt.show()

    def generate_dataframe(self, signal_power):
        possible_pairs = all_possible_pairs(self._nodes.keys())
        list_of_paths = []
        for pair in possible_pairs:
            pair_paths = self.find_paths(pair[0], pair[1])
            list_of_paths.append(pair_paths)
        all_signal_power = []
        all_signal_latency = []
        all_signal_noise = []
        all_signal_ratio = []
        all_path = []

        for paths in list_of_paths:
            for path in paths:
                # print(path)
                signal = Signal_information(signal_power, path)
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

        df = pd.DataFrame({
            "Path": all_path,
            "Total_latency": all_signal_latency,
            "Total_noise": all_signal_noise,
            "Signal_noise_ratio": all_signal_ratio
        })

        return df


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
    net.draw()

    signal_test = Signal_information(0.001, ['B', 'A'])
    net.propagate(signal_test)
    print("Power of the signal: {}".format(signal_test.signal_power))
    print("Latency of the signal: {}".format(signal_test.latency))
    print("Noise of the signal: {}".format(signal_test.noise_power))
    print("Path of the signal: {}".format(signal_test.path))

    data_frame = net.generate_dataframe(0.001)
    print(data_frame.tail(10))
    data_frame.to_csv('./data/lab3_dataframe.csv')
