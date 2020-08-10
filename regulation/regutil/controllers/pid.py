import time


class PID:
    """
    This class implements the PID algorithm.
    """

    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.target = 0

        self.e0 = 0
        self.esum = 0

    def calculate(self, measurement, dt):
        e = self.target - measurement
        de = (e - self.e0) / dt
        self.esum += e * dt

        self.e0 = e

        p = self.kp * e
        i = self.ki * self.esum
        d = self.kd * de

        c = p + i + d
        return c, p, i, d
