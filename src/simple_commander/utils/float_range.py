"""Helpful utils"""

def float_range(x, low, high, strong=True):
    """ Check if x is between low and high values.
        It works for int and float ranges."""
    if strong:
        result = low <= x <= high
    else:
        result = low < x < high
    return result