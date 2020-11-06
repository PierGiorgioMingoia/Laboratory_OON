class Connection(object):
    def __init__(self, inp, out, signal_power):
        self._input = inp
        self._output = out
        self._signal_power = signal_power
        self._latency = 0
        self._snr = 0

    @property
    def input(self):
        return self._input

    @property
    def output(self):
        return self._output

    @property
    def signal_power(self):
        return self._signal_power

    @property
    def latency(self):
        return self._latency

    @latency.setter
    def latency(self, latency):
        self._latency = latency

    @property
    def snr(self):
        return self._snr

    @snr.setter
    def snr(self, snr):
        self._snr = snr
