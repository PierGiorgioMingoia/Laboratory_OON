import numpy as np
import json
import matplotlib.pyplot as plt
import random
import itertools
import pandas as pd
from scipy.constants import c


class SignalInformation(object):
    def __init__(self, signal_power, path, latency=None, noise_power=None):
        self._signal_power = signal_power
        self._path = path
        if noise_power:
            self._noise_power = noise_power
        else:
            self._noise_power = 0
        if latency:
            self._latency = latency
        else:
            self._latency = 0

    @property
    def signal_power(self):
        return self._signal_power

    @property
    def noise_power(self):
        return self._noise_power

    @noise_power.setter
    def noise_power(self, noise):
        self._noise_power = noise

    @property
    def latency(self):
        return self._latency

    @latency.setter
    def latency(self, latency):
        self._latency = latency

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    def update_signal_power(self, increment):
        self._signal_power += increment

    def update_noise_power(self, increment):
        self._noise_power += increment

    def update_latency(self, increment):
        self._latency += increment

    def update_path(self):
        self._path.pop(0)
        # self._path = self._path[1:]


class Node(object):
    def __init__(self, node_dict):
        # for key, value in d.items():
        #    setattr(self, key, value)
        # self._successive = dict()
        self._label = node_dict['label']
        self._position = node_dict['position']
        self._connected_nodes = node_dict['connected_nodes']
        self._successive = {}

    @property
    def label(self):
        return self._label

    @property
    def position(self):
        return self._position

    @property
    def connected_nodes(self):
        return self._connected_nodes

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, successive):
        self._successive = successive

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
                signal_information = next_line.propagate(signal_information)
            else:
                print('Invalid Path')
        return signal_information


class Line(object):
    def __init__(self, label, length):
        self._label = label
        self._length = length
        self._successive = dict()
        self._state = 'free'

    @property
    def label(self):
        return self._label

    @property
    def length(self):
        return self._label

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, successive):
        self._successive = successive

    def latency_generation(self):
        latency = self._length / (c * 2 / 3)
        return latency

    def noise_generation(self, signal_power):
        noise = 1e-3 * signal_power * self._length
        return noise

    def propagate(self, signal_information):
        # Update latency
        lat_update = self.latency_generation()
        signal_information.update_latency(lat_update)

        # Update noise
        noise_update = self.noise_generation(signal_information.signal_power)
        signal_information.update_noise_power(noise_update)

        signal_information = self._successive[signal_information.path[0]].propagate(signal_information)
        return signal_information


class Network(object):
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
        self.connect()
        self._weighted_paths = pd.DataFrame({})

    @property
    def nodes(self):
        return self._nodes

    @property
    def lines(self):
        return self._lines

    @property
    def weighted_paths(self):
        return self._weighted_paths

    @weighted_paths.setter
    def weighted_paths(self, weighted_paths):
        self._weighted_paths = weighted_paths

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

    def sol_find_path(self, label1, label2):
        cross_nodes = [key for key in self.nodes.keys()
                       if ((key != label1) & (key != label2))]
        cross_lines = self.lines.keys()
        inner_paths = {'0': label1}
        for i in range(len(cross_nodes) + 1):
            inner_paths[str(i + 1)] = []
            for inner_path in inner_paths[str(i)]:
                inner_paths[str(i + 1)] += [inner_path +
                                            cross_node for cross_node in cross_nodes
                                            if ((inner_path[-1] + cross_node in cross_lines) &
                                                (cross_node not in inner_path))]
        paths = []
        for i in range(len(cross_nodes) + 1):
            for path in inner_paths[str(i)]:
                if path[-1] + label2 in cross_lines:
                    paths.append(path + label2)
        return paths

    def propagate(self, signal_information):
        propagated_signal_information = self._nodes[signal_information.path[0]].propagate(signal_information)
        return propagated_signal_information

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
            pos_x = self._nodes[key].position[0]
            pos_y = self._nodes[key].position[1]
            x.append(pos_x)
            y.append(pos_y)
            plt.text(pos_x + 20, pos_y + 20, key)
        plt.plot(x, y, marker='o', color='b', linestyle='')
        plt.title('Network')
        plt.show()

    def generate_dataframe(self, signal_power):
        possible_pairs = all_pairs(self._nodes.keys())
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
                signal = SignalInformation(signal_power, path)
                string_path = ''
                for node in path:
                    string_path += node + '->'
                string_path = string_path[:-2]
                all_path.append(string_path)
                self.propagate(signal)
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

    def find_best_snr(self, label1, label2):
        df = self.filter_dataframe_by_path(label1, label2)
        column = df['Signal_noise_ratio']
        max_index = column.idxmax()
        paths = df['Path']
        path = paths[max_index]
        return path.split('->')

    def find_best_latency(self, label1, label2):
        df = self.filter_dataframe_by_path(label1, label2)
        column = df['Total_latency']
        max_index = column.idxmin()
        paths = df['Path']
        path = paths[max_index]
        return path.split('->')

    def filter_dataframe_by_path(self, label1, label2):
        df = self.weighted_paths.loc[(self.weighted_paths['Path'].apply(lambda x: x.startswith(label1))) & (
            self.weighted_paths['Path'].apply(lambda x: x.endswith(label2)))]
        return df

    def stream(self, connections, label='latency'):
        for connection in connections:
            if label == 'latency':
                path = self.find_best_latency(connection.input, connection.output)
            else:
                path = self.find_best_snr(connection.input, connection.output)
            signal_information = SignalInformation(connection.signal_power, path)
            self.propagate(signal_information)
            connection.latency = signal_information.latency
            connection.snr = signal_to_noise_ratio(signal_information.signal_power, signal_information.noise_power)


class Connection(object):
    def __init__(self, inp, out, signal_power):
        self._input = inp
        self._output = out
        self._signal_power = signal_power
        self._latency = 0
        self._snr = 0

    @property
    def input(self):
        return self._input

    @property
    def output(self):
        return self._output

    @property
    def signal_power(self):
        return self._signal_power

    @property
    def latency(self):
        return self._latency

    @latency.setter
    def latency(self, latency):
        self._latency = latency

    @property
    def snr(self):
        return self._snr

    @snr.setter
    def snr(self, snr):
        self._snr = snr


def distance_nodes(x, y):
    return np.linalg.norm(np.array(x) - np.array(y))


def signal_to_noise_ratio(signal_power, noise):
    # Db = 10log10(w/w)
    return 10 * np.log10(signal_power / noise)


def all_possible_pairs(nodes):
    return list(itertools.combinations(nodes, 2))


def all_pairs(nodes):
    pairs = []
    for label1 in nodes:
        for label2 in nodes:
            if label1 != label2:
                pairs.append((label1, label2))
    return pairs


def plot_histogram(array, title):
    plt.hist(array, bins=10, color='#0504aa', alpha=0.7)
    plt.title('Histogram of {}'.format(title))
    plt.show()


def test_100_connections(network):
    c_array = []
    labels = ['A', 'B', 'C', 'D', 'E', 'F']
    for i in range(100):
        label1 = random.choice(labels)
        label2 = random.choice(labels)
        while label1 == label2:
            label2 = random.choice(labels)
        con = Connection(label1, label2, 1)
        c_array.append(con)
    network.stream(c_array, 'snr')
    return c_array


def histogram_of_connections(c_array):
    con_latency = []
    con_snr = []
    for connection in connections:
        print('Input: {}, Output: {}, Latency:{}, Snr: {}'.format(connection.input, connection.output,
                                                                  connection.latency, connection.snr))
        con_snr.append(connection.snr)
        con_latency.append(connection.latency)
    plot_histogram(con_latency, 'Latency')
    plot_histogram(con_snr, 'Signal to noise ratio')
    return con_latency, con_snr


if __name__ == '__main__':
    net = Network('./data/nodes.json')
    weighted_paths_df = pd.read_csv('./data/lab3_dataframe.csv', index_col=0)
    net.weighted_paths = weighted_paths_df
    connections = test_100_connections(net)
    histogram_of_connections(connections)
