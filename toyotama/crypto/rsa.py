from math import ceil

import gmpy2
from toyotama.crypto.util import extended_gcd
from toyotama.util.log import Logger

log = Logger()


def common_modulus_attack(e1, e2, c1, c2, n):
    s1, s2, _ = extended_gcd(e1, e2)
    return pow(c1, s1, n) * pow(c2, s2, n) % n


def wieners_attack(e, n):
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

    for k, dg in conv_from_cfrac(rat_to_cfrac(e, n)):
        edg = e * dg
        phi = edg // k

        x = n - phi + 1
        if x % 2 == 0 and gmpy2.is_square((x // 2) ** 2 - n):
            g = edg - phi * k
            return dg // g
    return None


def lsb_decryption_oracle_attack(n, e, c, oracle, progress=True):
    """
    oracle: method
        decryption oracle
        c*2**e = (2*m)**e (mod n) >> oracle >> m&1
    """
    from fractions import Fraction

    lb, ub = 0, n
    C = c
    i = 0
    nl = n.bit_length()
    while ub - lb > 1:
        if progress:
            log.progress(f"{(100*i//nl):>3}% [{i:>4}/{nl}]")

        mid = Fraction(lb + ub, 2)
        C = C * pow(2, e, n) % n
        if oracle(C):
            lb = mid
        else:
            ub = mid
        i += 1

    return int(ceil(lb))
