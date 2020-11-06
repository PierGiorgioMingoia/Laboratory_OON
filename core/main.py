from classes import *
import pandas as pd

if __name__ == '__main__':
    net = Network('./data/nodes.json')
    weighted_paths_df = pd.read_csv('./data/lab3_dataframe.csv', index_col=0)
    net.weighted_paths = weighted_paths_df
    connections = test_100_connections(net)
    # histogram_of_connections(connections)
