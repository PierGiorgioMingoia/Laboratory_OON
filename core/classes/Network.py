from .utils import *
import matplotlib.pyplot as plt
import json
import pandas as pd
import copy
import random
from scipy.special import erfinv as ierfc
from .Node import Node
from .SignalInformation import SignalInformation, Lightpath
from .Line import Line, NUM_OF_CHANNELS
from .GlobalVariable import NOISE_BANDWIDTH


class Network(object):
    def __init__(self, json_file):
        self._nodes = dict()
        self._lines = dict()
        self._nodes_switching_matrix = dict()
        with open(json_file) as f:
            network_data = json.load(f)
        for key, value in network_data.items():
            node = Node({"label": key, **value})
            self._nodes[key] = node
            pos = value['position']
            self._nodes_switching_matrix[key] = value['switching_matrix']
            for n in value['connected_nodes']:
                label = key + n
                next_pos = network_data[n]['position']
                length = distance_nodes(pos, next_pos)
                line = Line(label, length)
                self._lines[label] = line
        self.connect()
        self._weighted_paths = pd.DataFrame({})
        self._route_space = pd.DataFrame({})

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
        self.route_space = self.generate_route_space_dataframe()
        # update the full available route space using dynamic switching matrix
        self.update_route_space()

    @property
    def route_space(self):
        return self._route_space

    @route_space.setter
    def route_space(self, route_space):
        self._route_space = route_space

    @property
    def nodes_switching_matrix(self):
        return self._nodes_switching_matrix

    def connect(self):
        for key in self._nodes:
            for k in self._lines:
                if k.startswith(key):
                    self._nodes[key].successive[k] = self._lines[k]
        for key in self._lines:
            for k in self._nodes:
                if key.endswith(k):
                    self._lines[key].successive[k] = self._nodes[k]
        self.restore_switching_matrix()

    # Recursive algorithm for finding all possible paths
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

    # Non recursive algorithm for all possible paths
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

    def propagate(self, lightpath):
        propagated_signal_information = self._nodes[lightpath.path[0]].propagate(lightpath)
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

    # Channel availability for paths
    def generate_route_space_dataframe(self):
        feature_list = list(range(NUM_OF_CHANNELS))
        indexes = range(len(self.weighted_paths))
        d = pd.DataFrame(1, index=indexes, columns=feature_list)
        return d

    def light_path_channel_is_free(self, index):
        free_channel = None
        for channel in range(NUM_OF_CHANNELS):
            if self.route_space[channel][index] == 1:
                free_channel = channel
                break
        return free_channel

    # Update with multiplication of all lines.channels and switching matrix
    def update_route_space(self):
        paths = self.weighted_paths['Path']
        index = 0
        for path in paths:
            path = path.split('->')
            channels = np.ones(NUM_OF_CHANNELS, dtype=int)
            for i in range(len(path)):
                if i != 0 and i != len(path) - 1 and i % 2 == 0:
                    channels *= self.lines[path[i - 1] + path[i]].state
                    channels *= self.nodes[path[i]].switching_matrix[path[i - 1]][path[i + 1]]
                elif i % 2 != 0 and i != len(path) - 1:
                    channels *= self.lines[path[i - 1] + path[i]].state
                    channels *= self.nodes[path[i]].switching_matrix[path[i - 1]][path[i + 1]]
                elif i != 0:
                    channels *= self.lines[path[i - 1] + path[i]].state

            self.route_space.loc[index] = channels
            index += 1

    def find_best_snr(self, label1, label2):
        df = self.filter_dataframe_by_path(label1, label2)
        df = df.sort_values(by='Signal_noise_ratio', ascending=False)
        max_snr = 0
        paths = df['Path']
        paths_indexes = df['Path'].index
        path = paths.iloc[max_snr].split('->')
        channel = self.light_path_channel_is_free(paths_indexes[max_snr])
        while channel is None:
            max_snr += 1
            if max_snr >= len(paths):
                # No path available
                return -1, None, None
            channel = self.light_path_channel_is_free(paths_indexes[max_snr])
            path = paths.iloc[max_snr].split('->')
        return path, channel, paths_indexes[max_snr]

    def find_best_latency(self, label1, label2):
        df = self.filter_dataframe_by_path(label1, label2)
        df = df.sort_values(by='Total_latency', ascending=True)
        min_lat = 0
        paths = df['Path']
        paths_indexes = paths.index
        path = paths.iloc[min_lat].split('->')
        channel = self.light_path_channel_is_free(paths_indexes[min_lat])
        while channel is None:
            min_lat += 1
            # No path available
            if min_lat >= len(paths):
                return -1, None, None
            channel = self.light_path_channel_is_free(paths_indexes[min_lat])
            path = paths.iloc[min_lat].split('->')  # maybe can be put outside the while loop
        return path, channel, paths_indexes[min_lat]

    def filter_dataframe_by_path(self, label1, label2):
        df = self.weighted_paths.loc[(self.weighted_paths['Path'].apply(lambda x: x.startswith(label1))) & (
            self.weighted_paths['Path'].apply(lambda x: x.endswith(label2)))]
        return df

    def stream(self, connections, label='latency'):
        for connection in connections:
            if label == 'latency':
                path, channel, index = self.find_best_latency(connection.input, connection.output)
            else:
                path, channel, index = self.find_best_snr(connection.input, connection.output)
            print(path, channel)

            if path != -1 and channel is not None:
                lightpath = Lightpath(signal_power=connection.signal_power, path=path, channel=channel)
                bit_rate = self.calculate_bit_rate(lightpath, self._nodes[path[0]].transceiver)
                if bit_rate != 0:
                    self.propagate(lightpath)
                    self.update_route_space()
                    connection.latency = lightpath.latency
                    connection.snr = signal_to_noise_ratio(lightpath.signal_power, lightpath.noise_power)
                    connection.bit_rate = bit_rate
                else:
                    connection.latency = None
            else:
                connection.latency = None
        self.restore_switching_matrix()

    def path_is_free(self, path):
        lines = lines_from_path(path)
        free = True
        for line in lines:
            if self.lines[line].state == 'occupied':
                free = False
                break
        return free

    def restore_switching_matrix(self):
        switching_matrix = self.nodes_switching_matrix
        for key in self.nodes:
            self.nodes[key].switching_matrix = Node.create_switching_matrix(switching_matrix[key])

    def calculate_bit_rate(self, lightpath, strategy):
        # gsnr = self.weighted_paths.loc[
        #    self.weighted_paths['Path'] == '->'.join(lightpath.path)]['Signal_noise_ratio'].values[0]
        test_lightpath = copy.deepcopy(lightpath)
        self.propagate(test_lightpath)
        gsnr = signal_to_noise_ratio(test_lightpath.signal_power, test_lightpath.noise_power)
        del test_lightpath
        bit_rate = 0
        bit_error_ratio = 1e-3
        symbol_rate = lightpath.Rs

        if strategy == 'flex_rate':
            if gsnr < 2 * (ierfc(2 * bit_error_ratio) ** 2) * symbol_rate / NOISE_BANDWIDTH:
                bit_rate = 0
            elif 2 * (ierfc(2 * bit_error_ratio) ** 2) * symbol_rate / NOISE_BANDWIDTH <= gsnr < 14 / 3 * (
                    (ierfc(3 / 2 * bit_error_ratio) ** 2)) * symbol_rate / NOISE_BANDWIDTH:
                bit_rate = 100e9

            elif 14 / 3 * (ierfc(3 / 2 * bit_error_ratio) ** 2) * symbol_rate / NOISE_BANDWIDTH <= gsnr < 10 * (
                    (ierfc(8 / 3 * bit_error_ratio) ** 2)) * symbol_rate / NOISE_BANDWIDTH:
                bit_rate = 200e9
            #
            elif gsnr >= 10 * (ierfc(8 / 3 * bit_error_ratio) ** 2) * symbol_rate / NOISE_BANDWIDTH:
                bit_rate = 400e9

        elif strategy == 'shannon':
            bit_rate = 2 * symbol_rate * np.log2(1 + gsnr * NOISE_BANDWIDTH / symbol_rate)
        # fix-rate default
        else:
            if gsnr > 2 * (ierfc(2 * bit_error_ratio) ** 2) * symbol_rate / NOISE_BANDWIDTH:
                bit_rate = 100e9
            else:
                bit_rate = 0

        return bit_rate

    def create_traffic_matrix(self, M=1):
        traffic_matrix = {}
        for label in self.nodes:
            traffic_matrix[label] = {}
            for inner_label in self.nodes:
                bit_rate_request = 100e9 * M
                if label == inner_label:
                    bit_rate_request = 0
                traffic_matrix[label][inner_label] = bit_rate_request
        return traffic_matrix

    def creates_handle_connection_from_traffic_matrix(self, traffic_matrix):
        traffic_matrix_tmp = copy.deepcopy(traffic_matrix)
        for keys in list(traffic_matrix):
            for inner_keys in list(traffic_matrix[keys]):
                if traffic_matrix[keys][inner_keys] == 0:
                    del traffic_matrix_tmp[keys][inner_keys]
            if bool(traffic_matrix_tmp[keys]) is False:
                del traffic_matrix_tmp[keys]

        if bool(traffic_matrix_tmp):
            input_node = random.choice(list(traffic_matrix_tmp.keys()))
            output_node = random.choice(list(traffic_matrix_tmp[input_node].keys()))
            connection = Connection(input_node, output_node, 0.001)
            connections = [connection]
            self.stream(connections, 'snr')
            traffic_matrix[input_node][output_node] -= connection.bit_rate
            return connection
        else:
            return Connection('A', 'B', 0.001)

    pass
