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
        # TODO check if destination
        if len(signal_information.path) == 1:
            print("END OF PROPAGATION")
        else:
            next_line = self.successive[signal_information.path[0]]
            signal_information.update_path()
            next_line.propagate(signal_information)


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
        noise = 1 ** (np.exp(1) * signal_power * self.length)
        return noise

    def propagate(self, signal_information):
        lat_update = self.latency_generation()
        noise_update = self.noise_generation()
        signal_information.update_noise_power(noise_update)
        signal_information.update_latency(lat_update)
        self.successive.propagate(signal_information)


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

    def count_path_util(self, u, d, visited, path, paths):
        visited[u] = True
        path.append(u)

        if u == d:
            print(path)
            paths.append(path)
        else:
            for k in self.nodes[u].successive:
                if not visited[k[1]]:
                    self.count_path_util(k[1], d, visited, path, paths)
        path.pop()
        visited[u] = False

    def propagate(self, signal_information):
        pass

    def draw(self):
        x = []
        y = []
        for key in self.lines:
            print(key)
            x_values = [self.nodes[key[0]].position[0], self.nodes[key[1]].position[0]]
            y_values = [self.nodes[key[0]].position[1], self.nodes[key[1]].position[1]]
            plt.plot(x_values, y_values, linestyle='--', color='r')
        for key in self.nodes:
            print(key)
            x.append(self.nodes[key].position[0])
            y.append(self.nodes[key].position[1])
        plt.plot(x, y, marker='o', color='b', linestyle='')
        plt.show()


def distance_nodes(x, y):
    return np.linalg.norm(np.array(x) - np.array(y))


if __name__ == '__main__':
    net = Network('./data/nodes.json')
    net.connect()
    net.find_paths('C', 'B')
    net.draw()
