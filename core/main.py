from classes import *
import pandas as pd

if __name__ == '__main__':
    net = Network('./data/nodes_full_fixed_rate.json')
    weighted_paths_df = pd.read_csv('./data/lab3_dataframe_fix.csv', index_col=0)
    net.weighted_paths = weighted_paths_df
    connections = test_100_connections(net)

    snrs, bit_rates = lab8_histograms(connections)
    print_bit_rate_and_snr_average_and_total_c(snrs, bit_rates)

    # histogram_of_connections(connections)
    # print(net.route_space)
    # print(net.weighted_paths)
    # net.draw()
    # connection = test_2_connection('A', 'F', net)
