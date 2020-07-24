class MessageFormatError(Exception):
    pass

# TODO: Fill with more standard message formaters (Vector, IMU, Pose, etc.)


def format_test(a, b, c):
    test = {'a': a, 'b': b, 'c': c}
    return test

