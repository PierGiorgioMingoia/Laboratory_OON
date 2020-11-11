class Node(object):
    def __init__(self, node_dict):
        # for key, value in d.items():
        #    setattr(self, key, value)
        # self._successive = dict()
        self._label = node_dict['label']
        self._position = node_dict['position']
        self._connected_nodes = node_dict['connected_nodes']
        self._successive = {}

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
