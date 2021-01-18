from classes import *
import pandas as pd

if __name__ == '__main__':
    net = Network('./data/nodes_full_fixed_rate.json')
    weighted_paths_df = pd.read_csv('./data/lab10_dataframe.csv', index_col=0)
    net.weighted_paths = weighted_paths_df

    # connections = test_100_connections(net)
    # snrs, bit_rates = lab8_histograms(connections)
    # print_bit_rate_and_snr_average_and_total_c(connections)
    # net.draw()
    # connection = test_2_connection('A', 'F', net)

    traffic_matrix = net.create_traffic_matrix(M=5)
    display_traffic_matrix(traffic_matrix)
    conn, r, s = net.satisfy_traffic_matrix(traffic_matrix)
    print(len(conn), r, s)
    print(traffic_matrix)
    traffic_matrix_results_plot(conn, r, s)
    display_traffic_matrix(traffic_matrix)

    # df = net.generate_dataframe(0.001)
    # df.to_csv('./data/lab10_dataframe.csv')
