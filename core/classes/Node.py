import numpy as np
from .Line import NUM_OF_CHANNELS


class Node(object):
    def __init__(self, node_dict):
        self._label = node_dict['label']
        self._position = node_dict['position']
        self._connected_nodes = node_dict['connected_nodes']
        if 'transceiver' in node_dict:
            self._transceiver = node_dict['transceiver']
        else:
            self._transceiver = 'fixed-rate'
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

    @property
    def transceiver(self):
        return self._transceiver

    @transceiver.setter
    def transceiver(self, transceiver):
        self._transceiver = transceiver

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
                if hasattr(signal_information,
                           'last_crossed_node') and signal_information.last_crossed_node is not None:
                    self.dynamic_mod_switching_matrix(signal_information.channel, signal_information.last_crossed_node,
                                                      signal_information.path[1])
                signal_information.update_path(self.label)
                signal_information = next_line.propagate(signal_information)
            else:
                print('Invalid Path')
        return signal_information

    @staticmethod
    def create_switching_matrix(switching_matrix):
        for key in switching_matrix:
            for k in switching_matrix[key]:
                switching_matrix[key][k] = np.array(switching_matrix[key][k], dtype=np.uint8)
        return switching_matrix

    def dynamic_mod_switching_matrix(self, channel, input_node, output_node):
        self.switching_matrix[input_node][output_node][channel] = 0
        if channel == NUM_OF_CHANNELS - 1:
            self.switching_matrix[input_node][output_node][channel - 1] = 0
        elif channel == 0:
            self.switching_matrix[input_node][output_node][channel + 1] = 0
        else:
            self.switching_matrix[input_node][output_node][channel + 1] = 0
            self.switching_matrix[input_node][output_node][channel - 1] = 0
