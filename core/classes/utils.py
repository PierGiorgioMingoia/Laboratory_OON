import numpy as np
import matplotlib.pyplot as plt
import random
import itertools
import pandas as pd
from matplotlib.ticker import FixedLocator, FixedFormatter
from .Connection import Connection


def lines_from_path(path):
    lines = []
    for i in range(len(path) - 1):
        line = path[i] + path[i + 1]
        lines.append(line)
    return lines


def arrow_lines_from_path(path):
    lines = []
    for i in range(len(path) - 1):
        line = path[i] + '->' + path[i + 1]
        lines.append(line)
    return lines


def distance_nodes(x, y):
    return np.linalg.norm(np.array(x) - np.array(y))


def signal_to_noise_ratio(signal_power, noise):
    # Db = 10log10(w/w)
    return 10 * np.log10(signal_power / noise)


def db_to_linear(value):
    return 10 ** (value / 10)


def linear_to_db(value):
    return 10 * np.log10(value)


def all_possible_pairs(nodes):
    return list(itertools.combinations(nodes, 2))


def all_pairs(nodes):
    pairs = []
    for label1 in nodes:
        for label2 in nodes:
            if label1 != label2:
                pairs.append((label1, label2))
    return pairs


def plot_histogram(array, title, text=None, unit=None):
    plt.hist(array, bins=15, color='#0504aa', alpha=0.7)
    plt.title('Histogram of {}'.format(title))
    if text is not None:
        plt.suptitle(text, fontsize=10)
    if unit is not None:
        plt.xlabel(unit)
    plt.show()


def test_connections(network, n=100):
    c_array = []
    labels = ['A', 'B', 'C', 'D', 'E', 'F']
    for i in range(n):
        label1 = random.choice(labels)
        label2 = random.choice(labels)
        while label1 == label2:
            label2 = random.choice(labels)
        con = Connection(label1, label2, 0.001)
        c_array.append(con)
    network.stream(c_array, 'snr')
    return c_array


def histogram_of_connections(c_array):
    total_connections, c_array, refused_connections = count_connections(c_array)
    con_latency = []
    con_snr = []
    for connection in c_array:
        print('Input: {}, Output: {}, Latency:{}, Snr: {}'.format(connection.input, connection.output,
                                                                  connection.latency, connection.snr))
        if connection.latency is not None:
            con_snr.append(connection.snr)
            con_latency.append(connection.latency)
    # change from s to ms
    con_snr = [x for x in con_snr]
    con_latency = [x * 1000 for x in con_latency]
    plot_histogram(con_latency, 'Latency distribution',
                   text='Total connections: {} refused: {}'.format(total_connections, refused_connections), unit='ms')
    plot_histogram(con_snr, 'SNR distribution', unit='dB')
    return con_latency, con_snr


def count_connections(connections):
    total_connections = len(connections)
    accepted_connections = [c for c in connections if c.latency is not None]
    refused_connections = total_connections - len(accepted_connections)

    return total_connections, accepted_connections, refused_connections


def lab8_histograms(c_array):
    total_connections, c_array, refused_connections = count_connections(c_array)
    con_snr = []
    con_bit_rate = []
    for connection in c_array:
        con_snr.append(connection.snr)
        con_bit_rate.append(connection.bit_rate)
    con_bit_rate = [bit_rate_to_Giga_per_seconds(x) for x in con_bit_rate]
    plot_histogram(con_snr, 'SNR distribution',
                   text='Total connections: {} refused: {}'.format(total_connections, refused_connections), unit='dB')
    plot_histogram(con_bit_rate, 'Bit rate distribution', unit='Gbit/s')
    return con_snr, con_bit_rate


def bit_rate_to_Giga_per_seconds(bit_rate):
    return bit_rate / 1e9


def print_bit_rate_and_snr_average_and_total_c(connections):
    total_connections, connections, refused_connections = count_connections(connections)
    snrs = []
    bit_rates = []
    for connection in connections:
        snrs.append(connection.snr)
        bit_rates.append(connection.bit_rate)
    snrs = [x for x in snrs if x != 0]
    bit_rates = [bit_rate_to_Giga_per_seconds(bit_rate) for bit_rate in bit_rates if bit_rate != 0]
    print(
        'Total connections: {}, Refused connections: {}, Average SNR: {} dB, Average bit rate: {} Gbit/s, Total capacity: {} Gbit/s'.format(
            total_connections,
            refused_connections,
            np.average(snrs),
            np.average(bit_rates),
            np.sum(bit_rates)))
    return np.average(snrs), np.average(bit_rates), np.sum(bit_rates)


def print_all_lines_state(net):
    for line in net.lines:
        print(net.lines[line].state)


def test_2_connection(label1, label2, network):
    c_array = []
    con1 = Connection(label1, label2, 1)
    con2 = Connection(label1, label2, 1)
    c_array.append(con1)
    c_array.append(con2)
    network.stream(c_array, 'latency')
    return c_array


def print_full_pandas_df(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)


def create_traffic_matrix(network):
    traffic_matrix = {}
    for label in network.nodes:
        traffic_matrix[label] = {}
        for inner_label in network.nodes:
            bit_rate_request = 100e15
            if label == inner_label:
                bit_rate_request = 0
            traffic_matrix[label][inner_label] = bit_rate_request
    return traffic_matrix


def traffic_matrix_results_plot(conn, r, s):
    total_connections, conn, refused_connections = count_connections(conn)
    con_snrs = []
    con_latencies = []
    con_bit_rates = []
    for connection in conn:
        con_snrs.append(connection.snr)
        con_bit_rates.append(connection.bit_rate)
        con_latencies.append(connection.latency)
    con_snrs = [x for x in con_snrs]
    con_bit_rates = [bit_rate_to_Giga_per_seconds(bit_rate) for bit_rate in con_bit_rates]
    con_latencies = [x * 1000 for x in con_latencies]
    fig, axs = plt.subplots(2, 2, figsize=(20, 10), constrained_layout=True)
    fig.suptitle(
        'Traffic Matrix result, Total Connections: {}, Average SNR: {:.2f} dB, Average bit rate: {:.2f} Gbit/s, '
        'Total capacity: {:.2f} Gbit/s'.format(
            total_connections,
            np.average(con_snrs),
            np.average(con_bit_rates),
            np.sum(con_bit_rates)))
    axs[0, 0].hist(con_snrs, bins=20, color='#0504aa', alpha=0.7)
    axs[0, 0].set_title('Histogram of SNR distribution')
    axs[0, 0].set(xlabel='dB')
    axs[1, 0].hist(con_bit_rates, bins=10, color='#f59e42', alpha=0.7)
    axs[1, 0].set_title('Histogram of Bit rate distribution')
    axs[1, 0].set(xlabel='Gbit/s')
    axs[0, 1].hist(con_latencies, bins=20, color='#e342f5', alpha=0.7)
    axs[0, 1].set_title('Histogram of Latency distribution')
    axs[0, 1].set(xlabel='ms')
    bar1 = axs[1, 1].bar(['Satisfied', 'Refused'], [s, len(r)], color=['#14e00d', '#e00d0d'])
    for rect in bar1:
        height = rect.get_height()
        axs[1, 1].text(rect.get_x() + rect.get_width() / 2.0, height, '%d' % int(height), ha='center', va='bottom')
    axs[1, 1].set_title('Satisfied vs Refused requests')
    plt.show()


def display_traffic_matrix(traffic_matrix):
    n_nodes = len(traffic_matrix.keys())
    data_matrix = np.array([traffic_matrix[i][j] for i in traffic_matrix.keys() for j in traffic_matrix[i].keys()])
    data_matrix = data_matrix.reshape(n_nodes, n_nodes)
    fig, ax = plt.subplots(figsize=(7, 7))
    fig.suptitle('Traffic Matrix, Gbit/s')
    ax.set(ylabel='Origin node')
    ax.set(xlabel='Destination node')
    ax.xaxis.set_label_position('top')
    ax.matshow(data_matrix, cmap=plt.get_cmap('Reds'))
    for i in range(n_nodes):
        for j in range(n_nodes):
            c = data_matrix[j, i]
            ax.text(i, j, '{:.1f}'.format(bit_rate_to_Giga_per_seconds(c)), va='center', ha='center')

    x_labels = [item.get_text() for item in ax.get_xticklabels()]
    y_labels = [item.get_text() for item in ax.get_yticklabels()]
    nodes = list(traffic_matrix.keys())

    for i in range(len(nodes)):
        x_labels[i + 1] = nodes[i]
        y_labels[i + 1] = nodes[i]
    x_formatter = FixedFormatter(x_labels)
    y_formatter = FixedFormatter(y_labels)
    x_locator = FixedLocator(range(-1, 6))
    ax.xaxis.set_major_locator(x_locator)
    ax.xaxis.set_major_formatter(x_formatter)
    ax.yaxis.set_major_locator(x_locator)
    ax.yaxis.set_major_formatter(y_formatter)
    plt.show()
