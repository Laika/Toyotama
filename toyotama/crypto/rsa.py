"""RSA utility
"""

import typing
from math import ceil

import gmpy2
from toyotama.crypto.util import extended_gcd
from toyotama.util.log import Logger

log = Logger()


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


def wieners_attack(e: int, N: int) -> typing.Optional[int]:
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


def lsb_decryption_oracle_attack(
    N: int, e: int, c: int, oracle: typing.Callable, progress: bool = True
):
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
        if progress:
            log.progress(f"{(100*i//nl):>3}% [{i:>4}/{nl}]")

        mid = Fraction(lb + ub, 2)
        C = C * pow(2, e, N) % N
        if oracle(C):
            lb = mid
        else:
            ub = mid
        i += 1

    return ceil(lb)
