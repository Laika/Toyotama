"""Crypto Utility
"""
from functools import reduce
from math import ceil, gcd, isqrt, lcm
from operator import mul

import gmpy2

from ..util.log import get_logger

logger = get_logger()


def xor(*array: bytes, strict: bool = False) -> bytes:
    """XOR strings

    Calculate `A XOR B`.

    Args:
        A (bytes): A first string.
        B (bytes): A second string.
    Returns:
        bytes: The result of `A XOR B`.
    """

    if len(array) == 0:
        return None

    ret = bytes(len(array[0]))

    for block in array:
        ret = bytes(x ^ y for x, y in zip(ret, block, strict=strict))

    return ret


def rotl(data, shift: int, block_size: int = 16):
    """Rotate left
    Calculate ROTL
    """
    shift %= block_size
    return data[shift:] + data[:shift]


def rotr(data, shift: int, block_size: int = 16):
    """Rotate right
    Calculate ROTR
    """
    shift %= block_size
    return data[-shift:] + data[:-shift]


def i2b(x: int, byteorder="big") -> bytes:
    """Convert int to bytes.

    Args:
        x (int): A value.
        byteorder (str, optional): Byteorder. Defaults to "big".

    Returns:
        bytes: Result.
    """
    return x.to_bytes(x.bit_length() + 7 >> 3, byteorder=byteorder)


def b2i(x: bytes, byteorder="big") -> int:
    """Convert bytes to int.

    Args:
        x (bytes): A value.
        byteorder (str, optional): Byteorder. Defaults to "big".

    Returns:
        int: Result.
    """
    return int.from_bytes(x, byteorder=byteorder)


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Extended GCD.

    Args:
        a (int): The first value.
        b (int): The second value.
    Returns:
        tuple[int, int, int]: (x, y, g) s.t. Ax + By = gcd(A, B) = g
    """
    g, c = a, b
    x, a_ = 1, 0
    y, b_ = 0, 1

    while c != 0:
        q, m = divmod(g, c)
        g, c = c, m
        x, a_ = a_, x - q * a_
        y, b_ = b_, y - q * b_
    assert a * x + b * y == gcd(a, b)
    return x, y, g


def legendre(a: int, p: int) -> int:
    res = pow(a, (p - 1) // 2, p)
    return -1 if res == p - 1 else res


def mod_sqrt(a: int, p: int) -> int:
    """Mod Sqrt

    Compute x such that x*x == a (mod p)

    Args:
        a: The value.
        p: The modulus.
    Returns:
        int: `x` such that x*x == a (mod p).
    """
    if legendre(a, p) != 1:
        return 0
    if a == 0:
        return 0
    if p == 2:
        return p
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)

    s = p - 1
    e = (s & -s).bit_length() - 1
    s >>= e

    n = 2
    while legendre(n, p) != -1:
        n += 1

    x = pow(a, (s + 1) // 2, p)
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
            return x

        gs = pow(g, 1 << (r - m - 1), p)
        g = gs * gs % p
        x = x * gs % p
        b = b * g % p
        r = m


def chinese_remainder(a: list[int], m: list[int]) -> tuple[int, int]:
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
        a (list[int]): The list of value.
        m (list[int]): The list of modulus.
    Returns:
        tuple[int, int]: X, Y such that satisfy the equations
    """

    assert len(a) == len(m), "The length of a and m must be same."

    n = len(a)
    a1, m1 = a[0], m[0]
    for i in range(1, n):
        a2, m2 = a[i], m[i]
        g = gcd(m1, m2)
        if a1 % g != a2 % g:
            return 0, 0
        p, q, _ = extended_gcd(m1 // g, m2 // g)
        mod = lcm(m1, m2)
        a1 = (a1 * (m2 // g) * q + a2 * (m1 // g) * p) % mod
        m1 = mod

    return a1, m1


def bsgs(g, y, p, q=None):
    if not q:
        q = p
    m = ceil(isqrt(q))
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

        gmm *= gim
        gmm %= p

    return -1


def pohlig_hellman(g, y, factor):
    p = reduce(mul, factor) + 1
    x = [bsgs(pow(g, (p - 1) // q, p), pow(y, (p - 1) // q, p), p, q) for q in factor]

    x = chinese_remainder(x, factor)
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


def inverse(a: int, n: int) -> int:
    """Calculate modular inverse.

    Args:
        a (int): A value.
        n (int): A modulus.

    Returns:
        int: _description_
    """
    x, _, g = extended_gcd(a, n)
    if g != 1:
        logger.warning("No inverse for the given modulus.")
        return None

    return x % n


def solve_quadratic_equation(a: int, b: int, c: int) -> tuple[int, int]:
    D = b * b - 4 * a * c
    x = -b + isqrt(D) // (2 * a)
    xx = -b - isqrt(D) // (2 * a)

    return x, xx
