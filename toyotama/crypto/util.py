"""Crypto Utility
"""
from functools import reduce
from math import ceil, gcd, lcm
from operator import mul

import gmpy2


def i2b(x: int, byteorder="big"):
    return x.to_bytes(x.bit_length() + 7 >> 3, byteorder=byteorder)


def b2i(x: bytes, byteorder="big"):
    return int.from_bytes(x, byteorder=byteorder)


def extended_gcd(A: int, B: int) -> tuple[int, int, int]:
    """Extended GCD.

    Args:
        A (int): The first value.
        B (int): The second value.
    Returns:
        tuple[int, int, int]: (x, y, g) s.t. Ax + By = gcd(A, B) = g
    """
    g, c = A, B
    x, a = 1, 0
    y, b = 0, 1

    while c != 0:
        q, m = divmod(g, c)
        g, c = c, m
        x, a = a, x - q * a
        y, b = b, y - q * b
    assert A * x + B * y == gcd(A, B)
    return x, y, g


def mod_sqrt(a: int, p: int) -> int:
    """Mod Sqrt

    Compute x such that x*x == a (mod p)

    Args:
        a: The value.
        p: The modulus.
    Returns:
        int: `x` such that x*x == a (mod p).
    """
    if gmpy2.legendre(a, p) != 1:
        return 0
    elif a == 0:
        return 0
    elif p == 2:
        return 0
    elif p % 4 == 3:
        return pow(a, (p + 1) >> 2, p)

    s = p - 1
    e = (s & -s).bit_length() - 1
    s >>= e

    n = 2
    while gmpy2.legendre(n, p) != -1:
        n += 1

    x = pow(a, (s + 1) >> 1, p)
    b = pow(a, s, p)
    g = pow(n, s, p)
    r = e

    while True:
        t = b
        m = 0
        for m in range(r):
            if t == 1:
                break
            t = pow(t, 2, p)

        if m == 0:
            return x % p

        gs = pow(g, 1 << (r - m - 1), p)
        g = gs * gs % p
        x = x * gs % p
        b = b * g % p
        r = m


def chinese_remainder(A: list[int], M: list[int]) -> tuple[int, int]:
    """Chinese Remainder Theorem
    A = [a0, a1, a2, a3, ...]
    M = [m0, m1, m2, m3, ...]
    Compute X (mod Y = m0*m1*m2*...) such that these equations
        - x = a0 (mod m0)
        - x = a1 (mod m1)
        - x = a2 (mod m2)
        - x = a3 (mod m3)
        - ...
    by Garner's algorithm.

    Args:
        A (list[int]): The list of value.
        M (list[int]): The list of modulus.
    Returns:
        tuple[int, int]: X, Y such that satisfy the equations
    """

    assert len(A) == len(M), "numbers and moduli are not the same length."

    n = len(A)
    a1, m1 = A[0], M[0]
    for i in range(1, n):
        a2, m2 = A[i], M[i]
        g = gcd(m1, m2)
        if a1 % g != a2 % g:
            return 0, 0
        p, q, _ = extended_gcd(m1 // g, m2 // g)
        mod = lcm(m1, m2)
        a1 = (a1 * (m2 // g) * q + a2 * (m1 // g) * p) % mod
        m1 = mod

    return a1, m1


def baby_giant(g, y, p, q=None):
    if not q:
        q = p
    m = ceil(gmpy2.isqrt(q))
    table = {}
    b = 1
    for i in range(m):
        table[b] = i
        b = (b * g) % p

    gim = pow(pow(g, -1, p), m, p)
    gmm = y

    for i in range(m):
        if gmm in table.keys():
            return int(i * m + table[gmm])
        else:
            gmm *= gim
            gmm %= p

    return -1


def pohlig_hellman(g, y, factor):
    p = reduce(mul, factor) + 1
    X = [baby_giant(pow(g, (p - 1) // q, p), pow(y, (p - 1) // q, p), p, q) for q in factor]

    x = chinese_remainder(X, factor)
    return x


def factorize_from_kphi(n, kphi):
    """
    factorize by Miller-Rabin primality test
    n: p*q
    kphi: k*phi(n) = k*(p-1)*(q-1)

    kphi = 2**r * s
    """
    r = (kphi & -kphi).bit_length() - 1
    s = kphi >> r
    g = 1
    while g := int(gmpy2.next_prime(g)):
        x = pow(g, s, n)
        for _ in range(r):
            p = gcd(x - 1, n)
            if p != 1 and p != n:
                assert p * n // p == n
                return p, n // p
            x = x * x % n
    return None


def factorize_from_ed(n, d, e=0x10001):
    return factorize_from_kphi(n, e * d - 1)
