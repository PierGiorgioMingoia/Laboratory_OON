from .utils import *
import matplotlib.pyplot as plt
import json
import pandas as pd
from .Node import Node
from .SignalInformation import SignalInformation
from .Line import Line


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
        df = df.sort_values(by='Signal_noise_ratio', ascending=False)
        max_snr = 0
        paths = df['Path']
        path = paths.iloc[max_snr].split('->')
        while not self.path_is_free(path):
            max_snr += 1
            if max_snr >= len(paths):
                # No path available
                return -1
            path = paths.iloc[max_snr].split('->')
        return path

    def find_best_latency(self, label1, label2):
        df = self.filter_dataframe_by_path(label1, label2)
        df = df.sort_values(by='Total_latency', ascending=True)
        min_lat = 0
        paths = df['Path']
        path = paths.iloc[min_lat].split('->')
        while not self.path_is_free(path):
            min_lat += 1
            if min_lat >= len(paths):
                # No path available
                return -1
            path = paths.iloc[min_lat].split('->')
        return path

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
            # set the state of the lines of the path as occupied
            print(path)
            if path != -1:
                lines = lines_from_path(path)
                for line in lines:
                    self.set_line_occupied(line)

                signal_information = SignalInformation(connection.signal_power, path)
                self.propagate(signal_information)
                connection.latency = signal_information.latency
                connection.snr = signal_to_noise_ratio(signal_information.signal_power, signal_information.noise_power)
            else:
                connection.latency = None;

    def set_line_occupied(self, label):
        self.lines[label].state = 'occupied'

    def set_line_free(self, label):
        self.lines[label].state = 'free'

    def path_is_free(self, path):
        lines = lines_from_path(path)
        free = True
        for line in lines:
            if self.lines[line].state == 'occupied':
                free = False
                break
        return free
