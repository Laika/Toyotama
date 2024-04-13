"""Crypto Utility
"""
from functools import reduce
from logging import getLogger
from math import gcd, isqrt, lcm
from operator import mul
from random import randint
from typing import Literal

from toyotama.crypto.const import PRIMES

logger = getLogger(__name__)
Endian = Literal["big", "little"]


def int_to_bytes(x: int, byteorder: Endian = "big") -> bytes:
    """Convert integer to bytes.

    Args:
        x (int): A value.
        byteorder (str, optional): The byte order. Defaults to "big".

    Returns:
        bytes: The result of conversion.
    """
    return x.to_bytes(x.bit_length() + 7 >> 3, byteorder=byteorder)


def bytes_to_int(x: bytes, byteorder: Endian = "big") -> int:
    """Convert bytes to integer.

    Args:
        x (bytes): A value.
        byteorder (str, optional): The byte order. Defaults to "big".
    Returns:
        int: The result of conversion.
    """
    return int.from_bytes(x, byteorder=byteorder)


def is_prime(n: int, rounds: int = 10) -> bool:
    """Primality test.
    Args:
        n (int): A value.
        rounds (int, optional): The number of iteration. Defaults to 10.

    Returns:
        bool: Whether n is prime or not.
    """
    if n < 3 or n % 2 == 0:
        return n == 2
    for p in PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False
    return miller_rabin_Test(n, rounds)


def miller_rabin_Test(n: int, rounds: int = 10) -> bool:
    """Miller-Rabin primality test.

    Args:
        n (int): A value.
        k (int, optional): The number of iteration. Defaults to 10.

    Returns:
        bool: Whether n is prime or not.
    """
    if n < 2 or n % 2 == 0:
        return n == 2

    s, t = 0, n - 1
    while t % 2 == 0:
        s, t = s + 1, t >> 1

    done = set()
    for _ in range(min(rounds, n - 2)):
        a = randint(2, n - 1)
        while a in done:
            a = randint(2, n - 1)
        done.add(a)
        m = pow(a, t, n)
        if m == 1 or m == n - 1:
            continue

        is_composite = True
        for _ in range(s):
            m = (m * m) % n
            if m == 1:
                return False
            elif m == n - 1:
                is_composite = False
                break
        if is_composite:
            return False
    return True


def next_prime(x: int) -> int:
    """Get next prime number.

    Args:
        x (int): A value.
    Returns:
        int: The next prime number.
    """

    if x <= 1:
        return 2

    x += 1 + x % 2
    while not is_prime(x):
        x += 2

    return x


def xor(*array: bytes, strict: bool = False) -> bytes:
    """Calculate XOR of bytes.

    Args:
        array (bytes): The list of bytes.
        strict (bool, optional): Whether the length of each bytes is same or not. Defaults to False.

    Returns:
        bytes: The result of XOR.
    """

    if len(array) == 0:
        return b""

    ret = bytes(len(array[0]))

    for block in array:
        ret = bytes(x ^ y for x, y in zip(ret, block, strict=strict))

    return ret


def rotl(data: list, shift: int, block_size: int = 16) -> list:
    """Calculate ROTL
    Args:
        data (list): The list of value.
        shift (int): The shift value.
        block_size (int, optional): The block size. Defaults to 16.
    Returns:
        list: The result of rotation.
    """

    shift %= block_size
    return data[shift:] + data[:shift]


def rotr(data: list, shift: int, block_size: int = 16) -> list:
    """Calculate ROTR

    Args:
        data (list): The list of value.
        shift (int): The shift value.
        block_size (int, optional): The block size. Defaults to 16.
    Returns:
        list: The result of rotation.
    """
    shift %= block_size
    return data[-shift:] + data[:-shift]


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


def babystep_giantstep(g: int, y: int, p: int, q: int = 0) -> int:
    if not q:
        q = p

    m = isqrt(q)
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


bsgs = babystep_giantstep


def pohlig_hellman(g: int, y: int, factor: list[int]) -> tuple[int, int]:
    p = reduce(mul, factor) + 1
    x = [bsgs(pow(g, (p - 1) // q, p), pow(y, (p - 1) // q, p), p, q) for q in factor]

    res = chinese_remainder(x, factor)
    return res


def factorize_from_kphi(n: int, kphi: int) -> tuple[int, int]:
    """
    factorize by Miller-Rabin primality test
    n: p*q
    kphi: k*phi(n) = k*(p-1)*(q-1)

    kphi = 2**r * s
    """
    r = (kphi & -kphi).bit_length() - 1
    s = kphi >> r
    g = 1
    while g := int(next_prime(g)):
        x = pow(g, s, n)
        for _ in range(r):
            p = gcd(x - 1, n)
            if p != 1 and p != n:
                assert p * n // p == n
                return p, n // p
            x = x * x % n
    raise ValueError("factorization failed")


def factorize_from_ed(n: int, d: int, e: int = 0x10001) -> tuple[int, int]:
    return factorize_from_kphi(n, e * d - 1)


def inverse(a: int, n: int) -> int:
    """Calculate modular inverse.

    Args:
        a (int): A value.
        n (int): A modulus.

    Returns:
        int: _description_
    """
    return pow(a, -1, n)


def is_square(n: int):
    return isqrt(n) ** 2 == n


def solve_quadratic_equation(a: int, b: int, c: int) -> tuple[int, int]:
    D = b * b - 4 * a * c
    x = -b + isqrt(D) // (2 * a)
    xx = -b - isqrt(D) // (2 * a)

    return x, xx

