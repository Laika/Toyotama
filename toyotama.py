import binascii
import code
import os
import sys
from functools import reduce, singledispatch
from math import gcd, ceil, sqrt
from struct import pack, unpack
from time import sleep
from enum import IntEnum
import gmpy2

class Color(IntEnum) :
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    PURPLE = 93
    VIOLET = 128
    DEEP_PURPLE = 161
    ORANGE = 166

reset = '\x1b[0m'
bold  = '\x1b[1m'
fg    = lambda c: f'\x1b[38;5;{c}m'
bg    = lambda c: f'\x1b[48;5;{c}m'

message = lambda c, h, m : sys.stderr.write(f"{bold}{fg(c)}{h} {m}{reset}\n")
info  = lambda m: message(Color.BLUE, '[+]', m)
proc  = lambda m: message(Color.VIOLET, '[*]', m)
warn  = lambda m: message(Color.ORANGE, '[!]', m)
error = lambda m: message(Color.RED, '[-]', m)


# Utils
def interact(symboltable):
    code.interact(local=symboltable)


def show_variables(symboltable, *args):
    def getVarsNames(_vars, symboltable):
        return [getVarName(var, symboltable) for var in _vars]

    def getVarName(var, symboltable, error=None):
        for k, v in symboltable.items():
            if id(v) == id(var) :
                return k
        else:
            if error == "exception" :
                raise ValueError("Undefined function is mixed in subspace?")
            else:
                return error
    names = getVarsNames(args, symboltable)
    maxlen_name = max([len(name) for name in names])+1
    maxlen_type = max([len(type(value).__name__) for value in args])+3
    for name, value in zip(names, args):
        typ = f'<{type(value).__name__}>'
        if name.endswith('_addr'):
            info(f'{name.ljust(maxlen_name)}{typ.rjust(maxlen_type)}: {value:#x}')
        else:
            info(f'{name.ljust(maxlen_name)}{typ.rjust(maxlen_type)}: {value}')


@singledispatch
def extract_flag(s, head='{', tail='}', unique=True):
    raise TypeError('s must be str or bytes.')

@extract_flag.register(str)
def extract_flag_str(s, head='FLAG{', tail='}', unique=True):
    from re import compile, findall
    patt = f'{head}.*?{tail}'
    comp = compile(patt)
    flags = findall(comp, s)
    if unique:
        flags = set(flags)
    if not flags:
        error(f'The pattern {head}.*?{tail} does not exist.') 
        return None
    return flags

@extract_flag.register(bytes)
def extract_flag_bytes(s, head='FLAG{', tail='}', unique=True):
    from re import compile, findall
    patt = f'{head}.*?{tail}'.encode()
    comp = compile(patt)
    flags = findall(comp, s)
    if unique:
        flags = set(flags)
    if not flags:
        error(f'The pattern {head}.*?{tail} does not exist.') 
        return None
    return flags



def random_string(length, plaintext_space):
    from random import choice
    return ''.join([choice(plaintext_space) for _ in range(length)])


def int_to_string(x, byte=False):
    sb = x.to_bytes((x.bit_length()+7) // 8, 'big')
    if not byte:
        sb = sb.decode()
    return sb


@singledispatch
def string_to_int(s):
    raise TypeError('s must be str or bytes.')

@string_to_int.register(str)
def string_to_int_str(s):
    return int.from_bytes(s.encode(), 'big')

@string_to_int.register(bytes)
def string_to_int_bytes(s):
    return int.from_bytes(s, 'big')



def hexlify(x):
    if isinstance(x, str):
        x = x.encode()
    return binascii.hexlify(x).decode()

def unhexlify(x):
    if isinstance(x, str):
        x = x.encode()
    return binascii.unhexlify(x)


class Shell:
    def __init__(self, env=None):
        from subprocess import run, PIPE, DEVNULL
        self.__run = run
        self.__PIPE = PIPE
        self.__DEVNULL = DEVNULL
        self.env = env

    def run(self, command, output=True):
        from shlex import split
        command = split(command)
        if not output:
            ret = self.__run(command, stdout=self.__DEVNULL, stderr=self.__DEVNULL, env=self.env)
        else:
            ret = self.__run(command, stdout=self.__PIPE, stderr=self.__PIPE, env=self.env)
        return ret


class Connect:
    def __init__(self, target, mode='SOCKET', to=5.0, log=True, **args):
        if mode not in {'SOCKET', 'LOCAL'}:
            warn(f'Connect: {mode} is not defined.')
            info(f'Connect: Automatically set to "SOCKET".')
        self.mode = mode
        self.log = log
        self.is_alive = True
        
        if target.startswith('./'):
            target = {'program': target}
        elif target.startswith('nc'):
            _, host, port = target.split()
            target = {'host': host, 'port': int(port)}

        if self.mode == 'SOCKET':
            import socket
            host, port = target['host'], target['port']
            if self.log:
                proc(f'Connecting to {host}:{port}...')
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(to)
            self.sock.connect((host, port))
            self.timeout = socket.timeout
    
        elif self.mode == 'LOCAL':
            import subprocess
            program = target['program']
            self.wait = ('wait' in args and args['wait'])
            if self.log:
                proc(f'Starting {program} ...')
            self.proc = subprocess.Popen(program, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if self.log:
                info(f'PID: {self.proc.pid}')
            self.set_nonblocking(self.proc.stdout)
            self.timeout = None

    def set_nonblocking(self, fh):
        import fcntl
        fd = fh.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    def send(self, msg):
        if isinstance(msg, str):
            msg = msg.encode()
        if self.log:
            message('B', '[Send] <<', msg)
        try:
            if self.mode == 'SOCKET':
                self.sock.sendall(msg)
            elif self.mode == 'LOCAL':
                self.proc.stdin.write(msg)
        except Exception:
            self.is_alive = False

    def sendline(self, message):
        if isinstance(message, str):
            self.send(message + '\n')
        else:
            self.send(message + b'\n')

    def recv(self, n=2048):
        sleep(0.05)
        ret = b''
        try:
            if self.mode == 'SOCKET':
                ret = self.sock.recv(n)
            elif self.mode=='LOCAL':
                ret = self.proc.stdout.read(n)
        except Exception:
            pass

        if self.log:
            message('DP', '[Recv] >>', ret)
        return ret

    def recvuntil(self, term='\n'):
        ret = b''
        while not ret.endswith(term.encode()):
            try:
                if self.mode == 'SOCKET':
                    ret += self.sock.recv(1)
                elif self.mode == 'LOCAL':
                    ret += self.proc.stdout.read(1)
            except self.timeout:
                if not ret.endswith(term.encode()):
                    warn(f'readuntil: not end with {repr(term)} (timeout)')
                break
            except Exception:
                sleep(0.05)
        if self.log:
            message('DP', '[Recv] >>', ret)
        return ret

    def recvline(self):
        return self.recvuntil(term='\n')

    def interactive(self):
        from telnetlib import Telnet
        if self.log:
            info('Switching to interactive mode')
        with Telnet() as t:
            t.sock = self.sock
            t.mt_interact()

    def PoW(self, hashtype, match, pts, begin=False, hx=False):
        import hashlib
        match = match.decode().strip()
        x = b'a'
        i = 0
        if begin:
            proc(f'Searching x such that {hashtype}(x)[:{len(match)}] == {match} ...')
            while (h := hashlib.new(hashtype, x).hexdigest()[:len(match)]) != match:
                x = random_string(20, pts).encode()
        else:
            proc(f'Searching x such that {hashtype}(x)[-{len(match)}:] == {match} ...')
            while (h := hashlib.new(hashtype, x).hexdigest()[-(len(match)):]) != match:
                x = random_string(20, pts).encode()
    
        info(f'Found.  {hashtype}(\'{x.decode()}\') == {h}')
        if hx:
            x = hexlify(x)
        self.sendline(x)


    def __del__(self):
        if self.mode == 'SOCKET':
            self.sock.close()
            if self.log:
                proc('Disconnected.')

        elif self.mode == 'LOCAL':
            if self.wait:
                self.proc.communicate(None)
            elif self.proc.poll() is None:
                self.proc.terminate()

            if self.log:
                proc(f'Stopped.')
        if self.log:
            info('Press any key to close.')
            input()

def urlencode(s, encoding='shift-jis', safe=':/&?='):
    from urllib.parse import quote_plus
    return quote_plus(s, encoding=encoding, safe=safe)

def urldecode(s, encoding='shift-jis'):
    from urllib.parse import unquote_plus
    return unquote_plus(s, encoding=encoding)


    
# Pwn
## Utils
p8   = lambda x: pack('<B' if x > 0 else '<b', x)
p16  = lambda x: pack('<H' if x > 0 else '<h', x)
p32  = lambda x: pack('<I' if x > 0 else '<i', x)
p64  = lambda x: pack('<Q' if x > 0 else '<q', x)
u8   = lambda x, sign=False: unpack('<B' if not sign else '<b', x)[0] 
u16  = lambda x, sign=False: unpack('<H' if not sign else '<h', x)[0] 
u32  = lambda x, sign=False: unpack('<I' if not sign else '<i', x)[0] 
u64  = lambda x, sign=False: unpack('<Q' if not sign else '<q', x)[0] 
fill = lambda x, c='A', byte=True: (c*x).encode() if byte else c*x


# Crypto
## Utils
def lcm(x, y):
    return x*y // gcd(x, y)

def extended_gcd(a, b):
    c0, c1 = a, b
    a0, a1 = 1, 0
    b0, b1 = 0, 1

    while c1 != 0:
        q, m = divmod(c0, c1)
        c0, c1 = c1, m
        a0, a1 = a1, (a0 - q*a1)
        b0, b1 = b1, (b0 - q*b1)
    return a0, b0, c0


def mod_inverse(a, n):
    s, _, g = extended_gcd(a, n)
    if g != 1:
        raise Exception('The inverse does not exist.')
    return s % n


def mod_sqrt(a, p):
    if gmpy2.legendre(a, p) != 1:
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
    while gmpy2.legendre(n, p) != -1:
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


def rot(s, rotate=13):
    rotate %= 26
    r = ''
    for c in s:
        if 'A' <= c <= 'Z':
            r += chr((ord(c)-ord('A')+rotate)%26 + ord('A'))
        elif 'a' <= c <= 'z':
            r += chr((ord(c)-ord('a')+rotate)%26 + ord('a'))
        else:
            r += c
    return r


def xor_string(s, t):
    if isinstance(s, str):
        return ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(s, t))
    else:
        return bytes([a ^ b for a, b in zip(s, t)])


def get_secretkey(p, q, e=0x10001):
    return mod_inverse(e, (p-1) * (q-1))

def chinese_remainder(a, p):
    assert len(a) == len(p)
    P = reduce(lambda x, y: x*y, p)
    x = sum([ai * mod_inverse(P//pi, pi) * P // pi for ai, pi in zip(a, p)])
    return x % P


## Vigenere
def vigenere(cipher, key):
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
def common_modulus_attack(e1, e2, c1, c2, n):
    s1, s2, _ = extended_gcd(e1, e2)
    if s1 < 0:
        c1 = mod_inverse(c1, n)
        s1 *= -1
    if s2 < 0:
        c2 = mod_inverse(c2, n)
        s2 *= -1

    return (pow(c1, s1, n)*pow(c2, s2, n)) % n


## Wiener's Attack
def wieners_attack(e, n):
    def rat_to_cfrac(a, b):
        while b > 0:
            x = a // b
            yield x
            a, b = b, a - x*b
     
    def cfrac_to_rat_itr(cfrac):
        n0, d0 = 0, 1
        n1, d1 = 1, 0
        for q in cfrac:
            n = q*n1 + n0
            d = q*d1 + d0
            yield n, d
            n0, d0 = n1, d1
            n1, d1 = n, d
    
    def conv_from_cfrac(cfrac):
        n_, d_ = 1, 0
        for i, (n, d) in enumerate(cfrac_to_rat_itr(cfrac)):
            yield n + (i+1)%2 * n_, d + (i+1)%2 * d_
            n_, d_ = n, d    


    for k, dg in conv_from_cfrac(rat_to_cfrac(e, n)):
        edg = e * dg
        phi = edg // k

        x = n - phi + 1
        if x % 2 == 0 and gmpy2.is_square((x // 2)**2 - n):
            g = edg - phi*k
            return dg // g
    return None


def baby_giant(g, y, p):
    m = ceil(gmpy2.isqrt(p))
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


def pohlig_hellman(g, y, p, phi_p):
    X = [baby_giant(pow(g, (p-1)//q, p), pow(y, (p-1)//q, p), q)
         for q in phi_p]

    x = chinese_remainder(phi_p, X)
    return x
