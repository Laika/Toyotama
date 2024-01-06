import ctypes
import itertools
from functools import reduce
from logging import getLogger
from math import gcd

logger = getLogger(__name__)


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


class LibcRandom:
    def __init__(self, libc_path: str = "libc.so.6"):
        self.libc = ctypes.cdll.LoadLibrary(libc_path)
        self.libc.srand.argtypes = [ctypes.c_uint]
        self.libc.srand.restype = None
        self.libc.rand.argtypes = []
        self.libc.rand.restype = ctypes.c_int

    def srand(self, seed: int):
        self.libc.srand(seed)

    def rand(self):
        return self.libc.rand()
