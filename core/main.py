from classes import *
import pandas as pd

if __name__ == '__main__':
    net = Network('./data/nodes.json')
    weighted_paths_df = pd.read_csv('./data/lab3_dataframe.csv', index_col=0)
    net.weighted_paths = weighted_paths_df
    connections = test_100_connections(net)
    # net.draw()
    # histogram_of_connections(connections)
    print(net.route_space)
    print(net.weighted_paths)
    net.draw()
    # print(net.nodes['B'].switching_matrix['A']['A'])
