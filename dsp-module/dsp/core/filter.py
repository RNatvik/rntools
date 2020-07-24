class Filter:

    def __init__(self, b: list, a: list = None, k: float = 1):
        """
        Creates a filter object

        :param b: numerator coefficients of the transfer function (coeffs of X)
        :param a: denominator coefficients of the transfer function (coeffs of Y)
        :param k: output gain (default 1)
        """
        if not a:
            a = [1]
        self.b = b
        self.a = a
        self.k = k
        self.input = [0] * len(b)
        self.output = [0] * (len(a) - 1)

    def filter_value(self, x_new: float):
        """
        Passes a single value through the filter
        TODO: Find a better way to do the calculation than to use pop and insert for self.a[0]

        :param x_new: the value to be passed through the filter
        :return: the filter's output value
        """
        self.input = self._shift_list(self.input, x_new)
        a0 = self.a.pop(0)
        y_new = a0 * (
                sum([b * x for b, x in zip(self.b, self.input)])
                - sum([a * y for a, y in zip(self.a, self.output)])
        )
        self.a.insert(0, a0)
        self.output = self._shift_list(self.output, y_new)
        return y_new

    def filter_list(self, xn: list):
        """
        Passes a list of values through the filter

        :param xn: the input vector
        :return: the filter output vector
        """
        y = []
        for x in xn:
            y.append(self.filter_value(x))
        return y

    def clear(self):
        """
        Clear the filter's stored input and output list

        :return: None
        """
        self.input = [0] * len(self.input)
        self.output = [0] * len(self.output)

    def _shift_list(self, lst: list, val: float):
        lst.pop()
        lst.insert(0, val)
        return lst
