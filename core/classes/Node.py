import numpy as np


class Node(object):
    def __init__(self, node_dict):
        # for key, value in d.items():
        #    setattr(self, key, value)
        # self._successive = dict()
        self._label = node_dict['label']
        self._position = node_dict['position']
        self._connected_nodes = node_dict['connected_nodes']
        self._successive = {}
        self._switching_matrix = None

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

    @property
    def switching_matrix(self):
        return self._switching_matrix

    @switching_matrix.setter
    def switching_matrix(self, switching_matrix):
        self._switching_matrix = switching_matrix

    def propagate(self, signal_information):
        if len(signal_information.path) == 1:
            # print("END OF PROPAGATION")
            pass
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

    def create_switching_matrix(self):
        dic = dict()
        for node in self.connected_nodes:
            dic[node] = dict()
            for n in self.connected_nodes:
                if n == node:
                    dic[node][n] = np.zeros(10, dtype=int)
                else:
                    dic[node][n] = np.ones(10, dtype=int)
        return dic
