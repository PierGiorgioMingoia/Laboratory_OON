class SignalInformation(object):
    def __init__(self, signal_power=None, path=None, latency=None, noise_power=None):
        self._signal_power = signal_power
        self._path = path
        if noise_power:
            self._noise_power = noise_power
        else:
            self._noise_power = 0
        if latency:
            self._latency = latency
        else:
            self._latency = 0

    @property
    def signal_power(self):
        return self._signal_power

    @property
    def noise_power(self):
        return self._noise_power

    @noise_power.setter
    def noise_power(self, noise):
        self._noise_power = noise

    @property
    def latency(self):
        return self._latency

    @latency.setter
    def latency(self, latency):
        self._latency = latency

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    def update_signal_power(self, increment):
        self._signal_power += increment

    def update_noise_power(self, increment):
        self._noise_power += increment

    def update_latency(self, increment):
        self._latency += increment

    def update_path(self):
        self._path.pop(0)
        # self._path = self._path[1:]


class Lightpath(SignalInformation):

    def __init__(self, channel=None, *args, **kwargs):
        super(Lightpath, self).__init__(*args, **kwargs)
        self._channel = channel

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, channel):
        self._channel = channel
