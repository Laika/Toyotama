"""RSA utility
"""
from functools import reduce
from math import ceil, isqrt
from operator import mul
from typing import Callable

import gmpy2

from ..util.log import get_logger
from .util import extended_gcd, i2b, inverse

logger = get_logger()


def common_modulus_attack(e1: int, e2: int, c1: int, c2: int, N: int) -> int:
    """Common Modulus Attack

    Common Modulus Attack

    Args:
        e1 (int): The first public exponent.
        e2 (int): The second public exponent.
        c1 (int): The first ciphertext.
        c1 (int): The second ciphertext.
    Returns:
        int: The plaintext
    """
    s1, s2, _ = extended_gcd(e1, e2)
    return pow(c1, s1, N) * pow(c2, s2, N) % N


def wieners_attack(e: int, N: int) -> int | None:
    """Wiener's attack

    Wiener's attack

    Args:
        e (int): The public exponent.
        N (int): The modulus.
    Returns:
        int or None: The private key. None if failed.
    """

    def rat_to_cfrac(a, b):
        while b > 0:
            x = a // b
            yield x
            a, b = b, a - x * b

    def cfrac_to_rat_itr(cfrac):
        n0, d0 = 0, 1
        n1, d1 = 1, 0
        for q in cfrac:
            n = q * n1 + n0
            d = q * d1 + d0
            yield n, d
            n0, d0 = n1, d1
            n1, d1 = n, d

    def conv_from_cfrac(cfrac):
        n_, d_ = 1, 0
        for i, (n, d) in enumerate(cfrac_to_rat_itr(cfrac)):
            yield n + (i + 1) % 2 * n_, d + (i + 1) % 2 * d_
            n_, d_ = n, d

    for k, dg in conv_from_cfrac(rat_to_cfrac(e, N)):
        edg = e * dg
        phi = edg // k

        x = N - phi + 1
        if x % 2 == 0 and gmpy2.is_square((x // 2) ** 2 - N):
            g = edg - phi * k
            return dg // g
    return None


def lsb_decryption_oracle_attack(N: int, e: int, c: int, oracle: Callable, debug: bool = True) -> int:
    """Perform LSB Decryption oracle attack.

    Args:
        N (int): A modulus.
        e (int): A public exponent.
        c (int): A ciphertext.
        oracle (Callable): A decryption oracle. (2**e)*c = (2*m)**e (mod n) => oracle => m&1
        debug (bool, optional): Show debug log. Defaults to True.

    Returns:
        int: _description_
    """
    """LSB Decryption oracle attack

    Args:
        N (int): The modulus.
        e (int): The exponent.
        c (int): The ciphertext.
        oracle (Callable): The decryption oracle.  c*2**e = (2*m)**e (mod n) >> oracle >> m&1
    Returns:
        int: The plaintext
    """

    from fractions import Fraction

    lb, ub = 0, N
    C = c
    i = 0
    nl = N.bit_length()
    while ub - lb > 1:
        if debug:
            logger.info(f"{(100*i//nl):>3}% [{i:>4}/{nl}]")

        mid = Fraction(lb + ub, 2)
        C = C * pow(2, e, N) % N
        if oracle(C):
            lb = mid
        else:
            ub = mid
        i += 1

    return ceil(lb)


class RSASolver:
    def __init__(self):
        self.checkers = [self._check_wieners_attack, self._check_modulus]
        self.n = None
        self.e = None
        self.d = None
        self.m = None
        self.c = None
        self.factors = []
        self.phi = None
        self.kphi = None
        self.factorized = False

    def solve(self, plaintext: bool = True) -> int | bytes | None:
        for checker in self.checkers:
            checker()

        if self.factorized and self.e and self.n:
            self.phi = reduce(mul, (p**k - p ** (k - 1) for p, k in self.factors))
            self.d = inverse(self.e, self.phi)
            self.m = pow(self.c, self.d, self.n)
            if plaintext:
                return i2b(self.m)
            return self.m

        logger.warning("No solution found.")

    def _check_wieners_attack(self):
        if self.e is None or self.n is None:
            logger.warning("Either e or n is not set.")
        m = wieners_attack(self.e, self.n)
        if m:
            logger.info("Wiener's attack succeeded.")
            m = i2b(m)
            return m

    def _check_modulus(self):
        if self.n is None:
            logger.warning("n is not set.")
            return

        # Perfect root
        _p = isqrt(self.n)
        if _p**2 == self.n:
            self.add_factor(_p, 2)
            self.factorized = True

    def add_factor(self, p, k=1):
        self.factors.append((p, k))
