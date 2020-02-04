import binascii
import code
import os
import sys
from functools import reduce, singledispatch
from math import gcd, ceil, sqrt
from struct import pack, unpack
from time import sleep
import gmpy2

import log


# utils
def interact(symboltable):
    code.interact(local=symboltable)


def show_variables(symboltable, *args):
    def getvarsnames(_vars, symboltable):
        return [getvarname(var, symboltable) for var in _vars]

    def getvarname(var, symboltable, error=None):
        for k, v in symboltable.items():
            if id(v) == id(var) :
                return k
        else:
            if error == "exception" :
                raise valueerror("undefined function is mixed in subspace?")
            else:
                return error
    names = getvarsnames(args, symboltable)
    maxlen_name = max([len(name) for name in names])+1
    maxlen_type = max([len(type(value).__name__) for value in args])+3
    for name, value in zip(names, args):
        typ = f'<{type(value).__name__}>'
        if name.endswith('_addr'):
            log.info(f'{name.ljust(maxlen_name)}{typ.rjust(maxlen_type)}: {value:#x}')
        else:
            log.info(f'{name.ljust(maxlen_name)}{typ.rjust(maxlen_type)}: {value}')


@singledispatch
def extract_flag(s, head='{', tail='}', unique=True):
    raise typeerror('s must be str or bytes.')

@extract_flag.register(str)
def extract_flag_str(s, head='flag{', tail='}', unique=True):
    from re import compile, findall
    patt = f'{head}.*?{tail}'
    comp = compile(patt)
    flags = findall(comp, s)
    if unique:
        flags = set(flags)
    if not flags:
        log.error(f'the pattern {head}.*?{tail} does not exist.') 
        return None
    return flags

@extract_flag.register(bytes)
def extract_flag_bytes(s, head='flag{', tail='}', unique=True):
    from re import compile, findall
    patt = f'{head}.*?{tail}'.encode()
    comp = compile(patt)
    flags = findall(comp, s)
    if unique:
        flags = set(flags)
    if not flags:
        log.error(f'the pattern {head}.*?{tail} does not exist.') 
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
    raise typeerror('s must be str or bytes.')

@string_to_int.register(str)
def string_to_int_str(s):
    return int.from_bytes(s.encode(), 'big')

@string_to_int.register(bytes)
def string_to_int_bytes(s):
    return int.from_bytes(s, 'big')



@singledispatch
def hexlify(x):
    raise typeerror('x must be str or bytes.')

@hexlify.register(str)
def hexlify_str(x):
    x = x.encode()
    return binascii.hexlify(x).decode()

@hexlify.register(bytes)
def hexlify_bytes(x):
    return binascii.hexlify(x).decode()


@singledispatch
def unhexlify(x):
    raise typeerror('x must be str or bytes.')

@unhexlify.register(str)
def unhexlify_str(x):
    x = x.encode()
    return binascii.unhexlify(x)

@unhexlify.register(bytes)
def unhexlify_bytes(x):
    return binascii.unhexlify(x)

class shell:
    def __init__(self, env=None):
        from subprocess import run, pipe, devnull
        self.__run = run
        self.__pipe = pipe
        self.__devnull = devnull
        self.env = env

    def run(self, command, output=True):
        from shlex import split
        command = split(command)
        if not output:
            ret = self.__run(command, stdout=self.__devnull, stderr=self.__devnull, env=self.env)
        else:
            ret = self.__run(command, stdout=self.__pipe, stderr=self.__pipe, env=self.env)
        return ret


class connect:
    def __init__(self, target, mode='socket', to=5.0, verbose=True, **args):
        if mode not in {'socket', 'local'}:
            log.warn(f'connect: {mode} is not defined.')
            log.info(f'connect: automatically set to "socket".')
        self.mode = mode
        self.verbose = verbose
        self.is_alive = True
        
        if target.startswith('./'):
            target = {'program': target}
        elif target.startswith('nc'):
            _, host, port = target.split()
            target = {'host': host, 'port': int(port)}

        if self.mode == 'socket':
            import socket
            host, port = target['host'], target['port']
            if self.verbose:
                log.proc(f'connecting to {host}:{port}...')
            self.sock = socket.socket(socket.af_inet, socket.sock_stream)
            self.sock.settimeout(to)
            self.sock.connect((host, port))
            self.timeout = socket.timeout
    
        elif self.mode == 'local':
            import subprocess
            program = target['program']
            self.wait = ('wait' in args and args['wait'])
            if self.verbose:
                log.proc(f'starting {program} ...')
            self.proc = subprocess.popen(program, shell=False, stdin=subprocess.pipe, stdout=subprocess.pipe, stderr=subprocess.stdout)
            if self.verbose:
                log.info(f'pid: {self.proc.pid}')
            self.set_nonblocking(self.proc.stdout)
            self.timeout = None

    def set_nonblocking(self, fh):
        import fcntl
        fd = fh.fileno()
        fl = fcntl.fcntl(fd, fcntl.f_getfl)
        fcntl.fcntl(fd, fcntl.f_setfl, fl | os.o_nonblock)

    def send(self, msg):
        if isinstance(msg, str):
            msg = msg.encode()
        try:
            if self.mode == 'socket':
                self.sock.sendall(msg)
            elif self.mode == 'local':
                self.proc.stdin.write(msg)
            if self.verbose:
                log.message(log.color.blue, '[send] <<', msg)
        except exception:
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
            if self.mode == 'socket':
                ret = self.sock.recv(n)
            elif self.mode=='local':
                ret = self.proc.stdout.read(n)
        except exception:
            pass

        if self.verbose:
            log.message(log.color.deep_purple, '[recv] >>', ret)
        return ret

    def recvuntil(self, term='\n'):
        ret = b''
        while not ret.endswith(term.encode()):
            try:
                if self.mode == 'socket':
                    ret += self.sock.recv(1)
                elif self.mode == 'local':
                    ret += self.proc.stdout.read(1)
            except self.timeout:
                if not ret.endswith(term.encode()):
                    log.warn(f'readuntil: not end with {repr(term)} (timeout)')
                break
            except exception:
                sleep(0.05)
        if self.verbose:
            log.message(log.color.deep_purple, '[recv] >>', ret)
        return ret

    def recvline(self):
        return self.recvuntil(term='\n')

    def interactive(self):
        from telnetlib import telnet
        if self.verbose:
            log.info('switching to interactive mode')
        
        sleep(0.05)
        with telnet() as t:
            t.sock = self.sock
            t.mt_interact()

    def pow(self, hashtype, match, pts, begin=False, hx=False):
        import hashlib
        match = match.decode().strip()
        x = b'a'
        i = 0
        if begin:
            log.proc(f'searching x such that {hashtype}(x)[:{len(match)}] == {match} ...')
            while (h := hashlib.new(hashtype, x).hexdigest()[:len(match)]) != match:
                x = random_string(20, pts).encode()
        else:
            log.proc(f'searching x such that {hashtype}(x)[-{len(match)}:] == {match} ...')
            while (h := hashlib.new(hashtype, x).hexdigest()[-(len(match)):]) != match:
                x = random_string(20, pts).encode()
    
        log.info(f'found.  {hashtype}(\'{x.decode()}\') == {h}')
        if hx:
            x = hexlify(x)
        self.sendline(x)


    def __del__(self):
        if self.mode == 'socket':
            self.sock.close()
            if self.verbose:
                log.proc('disconnected.')

        elif self.mode == 'local':
            if self.wait:
                self.proc.communicate(None)
            elif self.proc.poll() is None:
                self.proc.terminate()

            if self.verbose:
                log.proc(f'stopped.')
        if self.verbose:
            log.info('press any key to close.')
            input()

def urlencode(s, encoding='shift-jis', safe=':/&?='):
    from urllib.parse import quote_plus
    return quote_plus(s, encoding=encoding, safe=safe)

def urldecode(s, encoding='shift-jis'):
    from urllib.parse import unquote_plus
    return unquote_plus(s, encoding=encoding)


    
# pwn
## utils
p8   = lambda x: pack('<b' if x > 0 else '<b', x)
p16  = lambda x: pack('<h' if x > 0 else '<h', x)
p32  = lambda x: pack('<i' if x > 0 else '<i', x)
p64  = lambda x: pack('<q' if x > 0 else '<q', x)
u8   = lambda x, sign=False: unpack('<b' if not sign else '<b', x)[0] 
u16  = lambda x, sign=False: unpack('<h' if not sign else '<h', x)[0] 
u32  = lambda x, sign=False: unpack('<i' if not sign else '<i', x)[0] 
u64  = lambda x, sign=False: unpack('<q' if not sign else '<q', x)[0] 
fill = lambda x, c='a', byte=True: (c*x).encode() if byte else c*x


# crypto
## utils
def lcm(x, y):
    return x*y // gcd(x, y)

def extended_gcd(a, b):
    c0, c1 = a, b
    a0, a1 = 1, 0
    b0, b1 = 0, 1

    while c1 != 0:
        q, m = divmod(c0, c1)
        c0, c1 = c1, m
        a0, a1 = a1, a0 - q*a1
        b0, b1 = b1, b0 - q*b1
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

@singledispatch
def xor_string(s, t):
    raise TypeError('Both s and t must be str or bytes.')
    
@xor_string.register(str)
def xor_string_str(s, t):
    return ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(s, t))

@xor_string.register(bytes)
def xor_string_bytes(s, t):
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

    return pow(c1, s1, n)*pow(c2, s2, n) % n


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

def factorize_from_ed(n, d, e=0x10001):
    k = e*d-1
    g = 1
    while g := int(gmpy2.next_prime(g)):
        t = k
        while t%2 == 0:
            t //= 2
            x = pow(g, t, n)
            if x > 1 and gcd(x-1, n) > 1:
                p = gcd(x-1, n)
                q = n//p
                return min(p, q), max(p, q)

