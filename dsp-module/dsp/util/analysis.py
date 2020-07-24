from math import cos, sin, atan2, pi, log


def get_frequency_response(b, a: list = None, k: float = 1, steps: int = 1001):
    """
    Calculates the frequency response of a given filter with coefficients a and b

    :param b: numerator coefficients of the transfer function (coeffs of X)
    :param a: denominator coefficients of the transfer function (coeffs of Y)
    :param k: output gain (default 1)
    :param steps: frequency resolution
    :return: magnitude, phase, normalized frequency
    """
    if not a:
        a = [0]
    A = len(a)
    B = len(b)
    W = [i / steps for i in range(steps)]
    magnitude = []
    phase = []
    for w in W:
        w *= pi
        ar = sum([ha * cos((1 - A + na) * w) for ha, na in zip(a, range(A))])
        br = sum([hb * cos((1 - B + nb) * w) for hb, nb in zip(b, range(B))])
        aj = sum([ha * sin((1 - A + na) * w) for ha, na in zip(a, range(A))])
        bj = sum([hb * sin((1 - B + nb) * w) for hb, nb in zip(b, range(B))])
        H = complex(br, bj) / complex(ar, aj)
        magnitude.append(k * abs(H))
        phase.append(-atan2(H.imag, H.real))
    return magnitude, phase, W


def amplitude2db(amp: list):
    """
    Convert amplitude to decibel scale

    :param amp: the amplitude
    :return: the amplitude as decibel
    """
    db = [20 * log(a, 10) for a in amp]
    return db


def db2amplitude(db: list):
    """
    Convert decibel to amplitude

    :param db: the decibel value
    :return: the amplitude value
    """
    amp = [pow(10, (d / 20)) for d in db]
    return amp
