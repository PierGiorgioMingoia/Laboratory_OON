import numpy as np
import math
from scipy.constants import c, h, e
from .utils import db_to_linear, linear_to_db

NUM_OF_CHANNELS = 10
KM_AMP = 80  # KM
GAIN = 16  # dB
NOISE_FIGURE = 3  # dB
ALPHA_DB = 0.2  # dB/km


class Line(object):
    def __init__(self, label, length):
        self._label = label
        self._length = length
        self._successive = dict()
        self._state = np.ones(NUM_OF_CHANNELS, dtype=int)
        self._n_amplifiers = math.ceil(length / (KM_AMP * 1000))
        if self._n_amplifiers < 2:
            self._n_amplifiers = 2
        self._n_span = self._n_amplifiers - 1
        self._gain = db_to_linear(GAIN)
        self._noise_figure = db_to_linear(NOISE_FIGURE)
        self._alfa = ALPHA_DB / (10 * np.log10(e))  # TODO ask if have to switch to from m to km
        self._beta2 = 2.13e-26
        self._gamma = 1.27

    @property
    def label(self):
        """Label of the line"""
        return self._label

    @property
    def length(self):
        """Length of the line"""
        return self._length

    @property
    def successive(self):
        """Successive Node"""
        return self._successive

    @successive.setter
    def successive(self, successive):
        self._successive = successive

    @property
    def state(self):
        """Channels of the Line"""
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def n_amplifiers(self):
        """Number of amplifier one each 80km, Booster and preamplifier included"""
        return self._n_amplifiers

    @n_amplifiers.setter
    def n_amplifiers(self, n_amplifiers):
        if n_amplifiers < 2:
            n_amplifiers = 2
        self._n_amplifiers = n_amplifiers
        self._n_span = self._n_amplifiers - 1

    @property
    def gain(self):
        return self._gain

    @gain.setter
    def gain(self, gain):
        self._gain = gain

    @property
    def noise_figure(self):
        return self._noise_figure

    @noise_figure.setter
    def noise_figure(self, noise_figure):
        self._noise_figure = noise_figure

    @property
    def alfa(self):
        """W/m Attenuation coefficient"""
        return self._alfa

    @property
    def beta2(self):
        """ps^2/km Chromatic dispersion"""
        return self._beta2

    @property
    def gamma(self):
        """(W m)^-1 Nonlinearity coefficient"""
        return self._gamma

    @property
    def n_span(self):
        """Number of strokes between amplifiers"""
        return self._n_span

    def latency_generation(self):
        latency = self.length / (c * 2 / 3)
        return latency

    def noise_generation(self, signal_power):
        noise = 1e-9 * signal_power * self._length
        return noise

    def propagate(self, signal_information):
        # Set line's channel as occupied
        if hasattr(signal_information, 'channel') and signal_information.channel is not None:
            self.set_channel_occupied(signal_information.channel)
        # Update latency
        lat_update = self.latency_generation()
        signal_information.update_latency(lat_update)

        # Update noise
        noise_update = self.noise_generation(signal_information.signal_power)
        signal_information.update_noise_power(noise_update)

        signal_information = self._successive[signal_information.path[0]].propagate(signal_information)
        return signal_information

    def change_channel_state(self, n):
        if self.state[n] == 1:
            self.state[n] = 0
        else:
            self.state[n] = 1

    def set_channel_occupied(self, channel_number):
        self.state[channel_number] = 0

    def set_channel_free(self, channel_number):
        self.state[channel_number] = 1

    def ase_generation(self):
        """Total amount of amplified spontaneous emissions (ASE)"""
        frequency = 193.414e12  # THz
        noise_bandwidth = 12.5e9  # GHz
        ase = self.n_amplifiers * (h * frequency * noise_bandwidth * self.noise_figure * (self.gain - 1))

        return ase

    def nli_generation(self, light_path):
        """Total amount generated by the nonlinear interface noise"""
        eta_nli = 16 / (27 * math.pi) * np.log(
            ((math.pi ** 2) / 2)
            * (self.beta2 * (light_path.Rs ** 2) / self.alfa)
            * (len(self.state) ** (2 * (light_path.Rs / light_path.df)))
        ) * ((self.gamma ** 2) / (4 * self.alfa * self.beta2)) * (1 / light_path.Rs ** 3)

        nli = (light_path.signal_power ** 3) * eta_nli * self.n_span
        return nli
