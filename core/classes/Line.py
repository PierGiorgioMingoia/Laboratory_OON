from scipy.constants import c


class Line(object):
    def __init__(self, label, length):
        self._label = label
        self._length = length
        self._successive = dict()
        self._state = 'free'

    @property
    def label(self):
        return self._label

    @property
    def length(self):
        return self._label

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, successive):
        self._successive = successive

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    def latency_generation(self):
        latency = self._length / (c * 2 / 3)
        return latency

    def noise_generation(self, signal_power):
        noise = 1e-3 * signal_power * self._length
        return noise

    def propagate(self, signal_information):
        # Update latency
        lat_update = self.latency_generation()
        signal_information.update_latency(lat_update)

        # Update noise
        noise_update = self.noise_generation(signal_information.signal_power)
        signal_information.update_noise_power(noise_update)

        signal_information = self._successive[signal_information.path[0]].propagate(signal_information)
        return signal_information
