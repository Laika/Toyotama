from functools import reduce
from gmpy2 import is_square, isqrt
from math import gcd, ceil, sqrt
from random import choice
from re import compile, findall
from string import ascii_letters, digits
from subprocess import PIPE, run
from typing import *
from pwn import *

def connect(command: str):
    host, port = command.split()[1:]
    return remote(host, port)

def extract_flag(s: str, head: str, tail: str = '') -> List[str]:
    try:
        comp = compile(rf'{head}.*?{tail}')
        return findall(comp, s)
    except:
        patt = f'{head}.*?{tail}'
        comp = compile(patt.encode())
        return findall(comp, s)

def random_string(n: int) -> str:
    return ''.join([choice(ascii_letters + digits) for _ in range(n)])


def lcm(x: int, y: int) -> int:
    return x * y // gcd(x, y)


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    c0, c1 = a, b
    a0, a1 = 1, 0
    b0, b1 = 0, 1

    while c1 != 0:
        q, m = divmod(c0, c1)
        c0, c1 = c1, m
        a0, a1 = a1, (a0 - q * a1)
        b0, b1 = b1, (b0 - q * b1)
    return a0, b0, c0



def mod_inverse(a: int, n: int) -> int:
    s, _, _ = extgcd(a, n)
    return s % n


def mod_sqrt(a, p):
    if legendre_symbol(a, p) != 1:
        return 0
    elif a == 0:
        return 0
    elif p == 2:
        return 0
    elif p % 4 == 3:
        return pow(a, (p + 1) / 4, p)

    s = p - 1
    e = 0
    while s % 2 == 0:
        s >>= 1
        e += 1

    n = 2
    while legendre_symbol(n, p) != -1:
        n += 1

    x = pow(a, (s + 1) / 2, p)
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

        gs = pow(g, 2 ** (r-m-1), p)
        g = (gs * gs) % p
        x = (x * gs) % p
        b = (b * g) % p
        r = m


def legendre_symbol(a, p):
    ls = pow(a, (p - 1) / 2, p)
    return -1 if ls == p-1 else ls


def int_to_string(x: int, byte=False) -> str:
    sb = x.to_bytes((x.bit_length() + 7) // 8, byteorder='big')
    if byte:
        return sb
    else:
        return sb.decode()



def string_to_int(s: str) -> int:
    return int.from_bytes(s.encode(), 'big')


def rot(n: int, s: str) -> str:
    n %= 26
    r = ''
    for c in s:
        if 'A' <= c <= 'Z':
            r += chr((ord(c) - ord('A') + n) % 26 + ord('A'))

        elif 'a' <= c <= 'z':
            r += chr((ord(c) - ord('a') + n) % 26 + ord('a'))
        else:
            r += c
    return r


def xor_string(s: str, t: str) -> str:
    if isinstance(s, str):
        return ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(s, t))
    else:
        return bytes([a ^ b for a, b in zip(s, t)])


def get_secretkey(e: int, p: int, q: int) -> int:
    return inv(e, (p - 1) * (q - 1))


def chinese_remainder(a: List[int], p: List[int]) -> int:
    P = reduce(lambda x, y: x * y, p)
    x = sum([ai * inv(P // pi, pi) * P // pi for ai, pi in zip(a, p)])
    return x % P

# Crypto

## Vigenere
def vigenere(cipher: str, key: str) -> str:
    key = key.lower()
    key = [ord('a') - ord(c) for c in key]
    ans = ''
    i = 0
    for c in cipher:
        if not c in ascii_letters:
            ans += c
            i += 1
        else:
            ans += rot(key[i % len(key)], c)
            i += 1
    return ''.join(ans)


## Common Modulus Attack
def common_modulus_attack(e1: int, e2: int, c1: int, c2: int, n: int) -> int:
    s1, s2, _ = extgcd(e1, e2)
    if s1 < 0:
        c1 = inv(c1, n)
        s1 *= -1
    if s2 < 0:
        c2 = inv(c2, n)
        s2 *= -1

    return (pow(c1, s1, n) * pow(c2, s2, n)) % n


## Wiener's Attack

def rat_to_cfrac(a: int, b: int) -> Iterator[int]:
    while b > 0:
        x = a // b
        yield x
        a, b = b, a - x * b


def cfrac_to_rat_itr(cfrac: Iterable[int]) -> Iterator[Tuple[int, int]]:
    n0, d0 = 0, 1
    n1, d1 = 1, 0
    for q in cfrac:
        n = q * n1 + n0
        d = q * d1 + d0
        yield n, d
        n0, d0 = n1, d1
        n1, d1 = n, d


def conv_from_cfrac(cfrac: Iterable[int]) -> Iterator[Tuple[int, int]]:
    n_, d_ = 1, 0
    for i, (n, d) in enumerate(cfrac_to_rat_itr(cfrac)):
        yield n + (i + 1) % 2 * n_, d + (i + 1) % 2 * d_
        n_, d_ = n, d


def wieners_attack(e: int, n: int) -> Optional[int]:
    for k, dg in conv_from_cfrac(rat_to_cfrac(e, n)):
        edg = e * dg
        phi = edg // k

        x = n - phi + 1
        print(is_square((x // 2)**2 - n))
        if x % 2 == 0 and is_square((x // 2)**2 - n):
            g = edg - phi * k
            return dg // g
    return None

## Discrete Logarithm Problem
## find x s.t. pow(g, x, p) == y


### Baby-step Giant-step algorithm
def baby_giant(g: int, y: int, p: int) -> int:
    m = ceil(isqrt(p))
    table = {}
    b = 1
    for i in range(m):
        table[b] = i
        b = (b * g) % p

    gim = inv(pow(g, m), p)
    gmm = y

    for i in range(m):
        if gmm in table.keys():
            return i * m + table[gmm]
        else:
            gmm *= gim
            gmm %= p

    return -1

## Pohlig-Hellman algorithm
def pohlig_hellman(g: int, y: int, p: int, phi_p: List[int]) -> int:
    print(phi_p)
    X = [baby_giant(pow(g, (p - 1) // q, p), pow(y, (p - 1) // q, p), q)
         for q in phi_p]

    x = chinese_remainder(phi_p, X)
    return x
