import time


class PID:

    def __init__(self, p, i, d, out_lim=None, i_lim=None, dt=None):
        self.p = p
        self.i = i
        self.d = d
        self.out_lim = out_lim
        self.i_lim = i_lim
        self.dt = dt

        self.target = 0
        self.e0 = 0
        self.e_sum = 0
        self.t0 = 0

        self.initialized = False

    def initialize(self, measurement):
        self.t0 = time.time()
        self.e0 = self.target - measurement
        self.initialized = True

    def calculate(self, measurement):
        if not self.initialized:
            self.initialize(measurement)
        # Set time since last calculation
        if self.dt:
            dt = self.dt
        else:
            t = time.time()
            dt = t - self.t0
            self.t0 = t

        # Calculate errors
        e = self.target - measurement
        de = e - self.e0
        self.e_sum += e
        if self.i_lim:
            self.e_sum = self._constrain(self.e_sum, self.i_lim[0], self.i_lim[1])
        self.e0 = e

        p = self.p * e
        i = self.i * self.e_sum * dt
        if dt > 0:
            d = self.d * de / dt
        else:
            d = 0
        output = p + i + d
        if self.out_lim:
            output = self._constrain(output, self.out_lim[0], self.out_lim[1])

        return output, p, i, d, dt

    def _constrain(self, value, minimum, maximum):
        return min(max(value, minimum), maximum)

