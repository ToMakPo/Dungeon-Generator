import sys

import numpy as np

MAX32 = np.iinfo(np.int32).max  # the upper limit of numpy int 32
MIN32 = np.iinfo(np.int32).min  # the lower limit of numpy int 32
SYS_MAX = sys.maxsize

def sum_lists(*lists):
    """
    Add together the values of multiple lists of numbers.
        >>> sum_lists([1, 2, 3, 4], [10, 20, 30], [100, 200, 300, 400, 500])
        [111, 222, 333, 404, 500]

    :param lists: a list of numbers
    :return: the summed results
    """

    if len(lists) == 0:
        return []

    l1 = lists[0]
    for l2 in lists[1:]:
        c1, c2 = len(l1), len(l2)
        d = c2 - c1
        if d > 0:
            l1 += [0]*d
        if d < 0:
            l2 += [0]*(d * -1)

        l1 = [x + y for (x, y) in zip(l1, l2)]
    return l1


def sum(*values):
    """
    Add all of the given vales together.

    :param values: the values to be summed
    :return: the total
    """
    total = 0
    for value in values:
        total += value
    return total


def clamp(value: int, low: int = 0, high: int = sys.maxsize) -> int:
    """
    Insure the value is always between the high and the low.
        >>> clamp(25, 20, 50)
        25
        >>> clamp(15, 20, 50)
        20
        >>> clamp(85, 20, 50)
        50
        >>> clamp(15, low=20)  # high is system max by default
        20
        >>> clamp(85, low=20)
        85
        >>> clamp(15, high=50)  # low is 0 by default
        15
        >>> clamp(85, high=50)
        50

    :param value: the value to be checked
    :param low: the minimum (inclusive) that the value can be (default 0)
    :param high: the maximum (inclusive) that the value can be (default system max)
    :return: a value that is between the high and the low
    """

    if value is None:  # returns None if the value is None
        return None
    if low is None:  # sets low to negative system max if low is None
        low = -sys.maxsize
    if high is None:  # sets high to positive system max if high is None
        high = sys.maxsize

    if low > high:  # insures low is less than high
        low, high = high, low

    if value < low:  # returns low if the value is less than low
        return low
    if value > high:  # returns high if the value is more than high
        return high
    return value


def clamp_float(value: float, low: float = 0, high: float = sys.maxsize) -> float:
    """
    Insure the value is always between the high and the low.

    :param value: the value to be checked
    :param low: the minimum (inclusive) that the value can be (default 0)
    :param high: the maximum (inclusive) that the value can be (default system max)
    :return: a value that is between the high and the low
    """

    if value is None:  # returns None if the value is None
        return None
    if low is None:  # sets low to negative system max if low is None
        low = -sys.maxsize
    if high is None:  # sets high to positive system max if high is None
        high = sys.maxsize

    if low > high:  # insures low is less than high
        low, high = high, low

    if value < low:  # returns low if the value is less than low
        return low
    if value > high:  # returns high if the value is more than high
        return high

    return value
