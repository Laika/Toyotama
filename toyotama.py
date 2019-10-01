from functools import reduce
from gmpy2 import is_square, isqrt, jacobi
from math import gcd, ceil, sqrt
from random import choice
from re import compile, findall
from string import ascii_letters, digits, ascii_uppercase, ascii_lowercase
from subprocess import Popen, PIPE, run
from typing import *
from pwn import remote
import sys
import code
import time
from colored import fg, attr
import binascii

reset = attr(0)
col1 = fg(128)
col2 = fg(93)
bold = attr(1)

# Utils
def connect(command: str):
    host, port = command.split()[1:]
    return remote(host, port)

def interact(symboltable):
    code.interact(local=symboltable)

def show_variables(symboltable, *args):
    def getVarsNames( _vars, symboltable ) :
        return [ getVarName( var, symboltable ) for var in _vars ]

    def getVarName( var, symboltable, error=None ) :
        for k,v in symboltable.items() :
            if id(v) == id(var) :
                return k
        else :
            if error == "exception" :
                raise ValueError("Undefined function is mixed in subspace?")
            else:
                return error
    names = getVarsNames(args, symboltable)
    maxlength = max([len(name+type(value).__name__) for name, value in zip(names, args)])
    for name, value in zip(names, args):
        typ = f'<{type(value).__name__}>'
        if name.endswith('_addr'):
            print(f'{col1}[#]{reset} {col2}{bold}{name+typ.rjust(maxlength)}: {reset}{value:#x}')
        else:
            print(f'{col1}[#]{reset} {col2}{bold}{name+typ.rjust(maxlength)}: {reset}{value}')



def extract_flag(s: str, head: str, tail: str = '', unique: bool = True) -> Set[str]:
    try:
        comp = compile(rf'{head}.*?{tail}')
        flags = findall(comp, s)
        if unique:
            flags = set(flags)
        return flags
    except:
        patt = f'{head}.*?{tail}'
        comp = compile(patt.encode())
        flags = findall(comp, s)
        if unique:
            flags = set(flags)
        return flags


def random_string(length: int) -> str:
    return ''.join([choice(ascii_letters + digits) for _ in range(length)])


def int_to_string(x: int, byte: bool = False) -> str:
    sb = x.to_bytes((x.bit_length()+7) // 8, 'big')
    if byte:
        return sb
    else:
        return sb.decode()


def string_to_int(s: str) -> int:
    return int.from_bytes(s.encode(), 'big')


def run_proc(filename: str):
    return Popen([f'./{filename}'], stdin=PIPE, stdout=PIPE, stderr=PIPE)

def send_query(proc, args: List) -> str:
    args = map(str, args)
    query = ' '.join(args)
    return proc.communicate(query.encode())[0].decode()

def hexlify(x):
    if isinstance(x, str):
        y = x.encode()
    else:
        y = x
    return binascii.hexlify(y).decode()

def unhexlify(x):
    if isinstance(x, str):
        y = x.encode()
    else:
        y = x
    return binascii.unhexlify(y)




# Pwn
## Utils


# Crypto
## Utils
def lcm(x: int, y: int) -> int:
    return x*y // gcd(x, y)

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    c0, c1 = a, b
    a0, a1 = 1, 0
    b0, b1 = 0, 1

    while c1 != 0:
        q, m = divmod(c0, c1)
        c0, c1 = c1, m
        a0, a1 = a1, (a0 - q*a1)
        b0, b1 = b1, (b0 - q*b1)
    return a0, b0, c0


def mod_inverse(a: int, n: int) -> int:
    s, _, _ = extended_gcd(a, n)
    return s % n


def mod_sqrt(a: int, p: int) -> int:
    if legendre_symbol(a, p) != 1:
        return 0
    elif a == 0:
        return 0
    elif p == 2:
        return 0
    elif p % 4 == 3:
        return pow(a, (p+1) / 4, p)

    s = p - 1
    e = 0
    while s % 2 == 0:
        s >>= 1
        e += 1

    n = 2
    while legendre_symbol(n, p) != -1:
        n += 1

    x = pow(a, (s+1) / 2, p)
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
        g = (gs*gs) % p
        x = (x*gs) % p
        b = (b*g) % p
        r = m


def rot(s: str, rotate: int = 13) -> str:
    rotate %= 26
    r = ''
    for c in s:
        if c in ascii_uppercase:
            r += chr((ord(c)-ord('A')+rotate)%26 + ord('A'))

        elif c in ascii_lowercase:
            r += chr((ord(c)-ord('a')+rotate)%26 + ord('a'))
        else:
            r += c
    return r


def xor_string(s: str, t: str) -> str:
    if isinstance(s, str):
        return ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(s, t))
    else:
        return bytes([a ^ b for a, b in zip(s, t)])


def get_secretkey(p: int, q: int, e: int = 0x10001) -> int:
    return mod_inverse(e, (p-1) * (q-1))


def chinese_remainder(a: List[int], p: List[int]) -> int:
    assert len(a) == len(p)
    P = reduce(lambda x, y: x*y, p)
    x = sum([ai * mod_inverse(P//pi, pi) * P // pi for ai, pi in zip(a, p)])
    return x % P


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
            ans += rot(c, key[i % len(key)])
            i += 1
    return ''.join(ans)


## Common Modulus Attack
def common_modulus_attack(e1: int, e2: int, c1: int, c2: int, n: int) -> int:
    s1, s2, _ = extended_gcd(e1, e2)
    if s1 < 0:
        c1 = mod_inverse(c1, n)
        s1 *= -1
    if s2 < 0:
        c2 = mod_inverse(c2, n)
        s2 *= -1

    return (pow(c1, s1, n)*pow(c2, s2, n)) % n


## Wiener's Attack
def rat_to_cfrac(a: int, b: int) -> Iterator[int]:
    while b > 0:
        x = a // b
        yield x
        a, b = b, a - x*b


def cfrac_to_rat_itr(cfrac: Iterable[int]) -> Iterator[Tuple[int, int]]:
    n0, d0 = 0, 1
    n1, d1 = 1, 0
    for q in cfrac:
        n = q*n1 + n0
        d = q*d1 + d0
        yield n, d
        n0, d0 = n1, d1
        n1, d1 = n, d


def conv_from_cfrac(cfrac: Iterable[int]) -> Iterator[Tuple[int, int]]:
    n_, d_ = 1, 0
    for i, (n, d) in enumerate(cfrac_to_rat_itr(cfrac)):
        yield n + (i+1)%2 * n_, d + (i+1)%2 * d_
        n_, d_ = n, d


def wieners_attack(e: int, n: int) -> Optional[int]:
    for k, dg in conv_from_cfrac(rat_to_cfrac(e, n)):
        edg = e * dg
        phi = edg // k

        x = n - phi + 1
        print(is_square((x // 2)**2 - n))
        if x % 2 == 0 and is_square((x // 2)**2 - n):
            g = edg - phi*k
            return dg // g
    return None


## Discrete Logarithm Problem
## find x s.t. pow(g, x, p) == y

## Baby-step Giant-step algorithm
def baby_giant(g: int, y: int, p: int) -> int:
    m = ceil(isqrt(p))
    table = {}
    b = 1
    for i in range(m):
        table[b] = i
        b = (b*g) % p

    gim = mod_inverse(pow(g, m), p)
    gmm = y

    for i in range(m):
        if gmm in table.keys():
            return i*m + table[gmm]
        else:
            gmm *= gim
            gmm %= p

    return -1


## Pohlig-Hellman algorithm
def pohlig_hellman(g: int, y: int, p: int, phi_p: List[int]) -> int:
    print(phi_p)
    X = [baby_giant(pow(g, (p-1)//q, p), pow(y, (p-1)//q, p), q)
         for q in phi_p]

    x = chinese_remainder(phi_p, X)
    return x
