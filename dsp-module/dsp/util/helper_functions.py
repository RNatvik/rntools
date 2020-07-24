from math import sin, pi


def generate_signal(f, fs, A, DC, t_final, t_steps=1000):
    """
    Generate a signal with specified specifications

    :param f: the signal's frequency
    :param fs: the sampling frequency
    :param A: the sine wave amplitude
    :param DC: an added dc component of the signal
    :param t_final: final time for signal.
    :param t_steps: number of steps for time vector
    :return: x(n), t(n), x(t), t
    """
    w = 2 * pi * f / fs
    T = [t_final * i / t_steps for i in range(t_steps)]
    N = int(t_final * fs)
    tn = [i / fs for i in range(N)]
    xn = [A * sin(w * n) + DC for n in range(N)]
    xt = [A * sin(2 * pi * f * t) + DC for t in T]
    return xn, tn, xt, T


def add_signals(sig1: list, sig2: list):
    """
    Sums two signal lists together

    :param sig1: signal 1
    :param sig2: signal 2
    :return: new summed signal
    """
    if len(sig1) != len(sig2):
        return None
    return [s1 + s2 for s1, s2 in zip(sig1, sig2)]
