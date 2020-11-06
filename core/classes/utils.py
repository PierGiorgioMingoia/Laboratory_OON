import numpy as np
import matplotlib.pyplot as plt
import random
import itertools
from .Connection import Connection


def lines_from_path(path):
    lines = []
    for i in range(len(path) - 1):
        line = path[i] + path[i + 1]
        lines.append(line)
    return lines


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
    network.stream(c_array, 'latency')
    return c_array


def histogram_of_connections(c_array):
    con_latency = []
    con_snr = []
    for connection in c_array:
        print('Input: {}, Output: {}, Latency:{}, Snr: {}'.format(connection.input, connection.output,
                                                                  connection.latency, connection.snr))
        con_snr.append(connection.snr)
        con_latency.append(connection.latency)
    plot_histogram(con_latency, 'Latency')
    plot_histogram(con_snr, 'Signal to noise ratio')
    return con_latency, con_snr
