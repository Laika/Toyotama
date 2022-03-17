import itertools
from functools import reduce
from math import gcd


def lcg_crack(X, A=None, B=None, M=None):
    n = len(X)
    if not M:
        if n >= 6:
            Y = [x - y for x, y in itertools.pairwise(X)]
            Z = [x * z - y * y for x, y, z in zip(Y, Y[1:], Y[2:])]
            M = abs(reduce(gcd, Z))

        elif n >= 3:
            assert A and B, "Can't crack"
            M = gcd(X[2] - A * X[1] - B, X[1] - A * X[0] - B)
        else:
            assert False, "Can't crack"

    if not A:
        if n >= 3:
            A = (X[2] - X[1]) * pow(X[1] - X[0], -1, M) % M

    if not B:
        if n >= 2:
            B = (X[1] - A * X[0]) % M

    return A, B, M
