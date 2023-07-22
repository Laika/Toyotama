import itertools
from functools import reduce
from math import gcd


def lcg_crack(x, a=None, b=None, m=None):
    n = len(x)
    if not m:
        if n >= 6:
            Y = [x - y for x, y in itertools.pairwise(x)]
            Z = [x * z - y * y for x, y, z in zip(Y, Y[1:], Y[2:])]
            m = abs(reduce(gcd, Z))

        elif n >= 3:
            assert a and b, "Can't crack"
            m = gcd(x[2] - a * x[1] - b, x[1] - a * x[0] - b)
        else:
            assert False, "Can't crack"

    if not a:
        if n >= 3:
            a = (x[2] - x[1]) * pow(x[1] - x[0], -1, m) % m

    if not b:
        if n >= 2:
            b = (x[1] - a * x[0]) % m

    return a, b, m
