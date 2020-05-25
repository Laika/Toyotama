import binascii
import code
import os
import sys
import threading
import subprocess
from functools import reduce, singledispatch
from math import gcd, ceil, sqrt
from struct import pack, unpack
from time import sleep
from enum import Enum

import gmpy2
import requests

import log
from integer import Int



# utils
def interact(symboltable):
    """Switch to interactive mode

    Parameters
    ----------
        symboltable: dict
            The symboltable when this function is called.

    Returns
    -------
    None

    Examples
    --------
    a = 5 + 100
    interact(globals())

    (InteractiveConsole)
    >>> a 
    105
    """


    code.interact(local=symboltable)
    


def show_variables(symboltable, *args):
    """Show the value and its type

    Parameters
    ----------
        symboltable: dict
            The symboltable when this function is called.

        *args
            The variable to show
            

    Returns
    -------
    None

    Examples
    --------
    >>> a = 5 + 100
    >>> b = 0x1001
    >>> system_addr = 0x08080808
    >>> s = 'hoge'
    >>> show_variables(globals(), a, b, system_addr, s)

    [+] a            <int>: 105
    [+] b            <int>: 4097
    [+] system_addr  <int>: 0x8080808
    [+] s            <str>: hoge
    """

    def getvarname(var, symboltable, error=None):
        for k, v in symboltable.items():
            if id(v) == id(var):
                return k
        else:
            if error == "Exception":
                raise ValueError("undefined function is mixed in subspace?")
            else:
                return error
    names = [getvarname(var, symboltable) for var in args]
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
    """Extract flags from a string

    Parameters
    ----------
    s: str or bytes
        Find flags from this string

    head: str  
        The head of flag format

    tail: str
        The tail of flag format


    Returns
    -------
    list
        The list of flags found in `s`

    """

    raise TypeError('s must be str or bytes.')

@extract_flag.register(str)
def extract_flag_str(s, head='{', tail='}', unique=True):
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
def extract_flag_bytes(s, head='{', tail='}', unique=True):
    from re import compile, findall
    patt = f'{head}.*?{tail}'.encode()
    comp = compile(patt)
    flags = findall(comp, s)
    if unique:
        flags = set(flags)
    if not flags:
        log.error(f'The pattern {head}.*?{tail} does not exist.') 
        return None
    return flags



def random_string(length, plaintext_space='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', byte=True):
    """ Generate random string

    Parameters
    ----------
    length: int
        Length of random string

    plaintext_space: iterable
        Each character is picked from `plaintext_space`


    Returns
    -------
    str
        Randomly picked string

    Examples
    --------
    >>> random_string(10, 'abcdefghijklmnopqrstuvwxyz')
    'jzhmajvqje'
    >>> random_string(10, 'abcdefghijklmnopqrstuvwxyz')
    'aghlqvucdf'
    """

    from random import choices
    rnd = choices(plaintext_space, k=length)
    if isinstance(plaintext_space, bytes):
        rnd = bytes(rnd)
    if isinstance(plaintext_space, str):
        rnd = ''.join(rnd)
    return rnd


def int_to_string(x, byte=False):
    """ Convert integer to string

    Parameters
    ----------
    x: int
        Integer

    byte: bool
        Keep it bytes or not

    Returns
    -------
    str (or bytes)
        Result

    Examples
    --------
    >>> int_to_string(8387236825053623156)
    'testtest'
    >>> int_to_string(8387236825053623156, byte=True)
    b'testtest'
    """

    res = bytes.fromhex(format(x, 'x'))
    if not byte:
        res = res.decode()
    return res


@singledispatch
def string_to_int(s):
    """ Convert string or bytes to integer

    Parameters
    ----------
    s: str (or bytes)
        String

    Returns
    -------
    int
        Result

    Examples
    --------
    >>> string_to_int('testtest')
    8387236825053623156
    >>> string_to_int(b'testtest')
    8387236825053623156
    """
    
    raise TypeError('s must be str or bytes.')

@string_to_int.register(str)
def string_to_int_str(s):
    return int.from_bytes(s.encode(), 'big')

@string_to_int.register(bytes)
def string_to_int_bytes(s):
    return int.from_bytes(s, 'big')


class Shell:
    def __init__(self, env=None):
        self.__run = subprocess.run
        self.__pipe = subprocess.PIPE
        self.__devnull = subprocess.DEVNULL
        self.env = env

    def run(self, command, output=True):
        from shlex import split
        command = split(command)
        if not output:
            ret = self.__run(command, stdout=self.__devnull, stderr=self.__devnull, env=self.env)
        else:
            ret = self.__run(command, stdout=self.__pipe, stderr=self.__pipe, env=self.env)
        return ret

class Mode(Enum):
    SOCKET = 1
    LOCAL = 2

class Connect:
    def __init__(self, target, mode=Mode.SOCKET, to=10.0, verbose=True, pause=True, **args):
        if mode not in Mode:
            log.warn(f'Connect: {mode} is not defined.')
            log.info(f'Connect: Automatically set to "SOCKET".')
        self.mode = mode
        self.verbose = verbose
        self.pause = pause
        self.is_alive = True
        
        if target.startswith('./'):
            target = {'program': target}
        elif target.startswith('nc'):
            _, host, port = target.split()
            target = {'host': host, 'port': int(port)}

        if self.mode == Mode.SOCKET:
            import socket
            host, port = target['host'], target['port']
            if self.verbose:
                log.proc(f'Connecting to {host}:{port}...')
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(to)
            self.sock.connect((host, port))
            self.timeout = socket.timeout
    
        elif self.mode == Mode.LOCAL:
            program = target['program']
            self.wait = ('wait' in args and args['wait'])
            if self.verbose:
                log.proc(f'Starting {program} ...')
            self.proc = subprocess.Popen(program, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if self.verbose:
                log.info(f'pid: {self.proc.pid}')
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
        try:
            if self.mode == Mode.SOCKET:
                self.sock.sendall(msg)
            elif self.mode == Mode.LOCAL:
                self.proc.stdin.write(msg)
            if self.verbose:
                log.message(log.Color.BLUE, '[Send] <<', msg)
        except Exception:
            self.is_alive = False

    def sendline(self, message):
        if isinstance(message, str):
            self.send(message + '\n')
        else:
            self.send(message + b'\n')

    def recv(self, n=2048, quiet=False):
        sleep(0.05)
        ret = b''
        try:
            if self.mode == Mode.SOCKET:
                ret = self.sock.recv(n)
            elif self.mode == Mode.LOCAL:
                ret = self.proc.stdout.read(n)
        except Exception:
            pass

        if not quiet and self.verbose:
            log.message(log.Color.DEEP_PURPLE, '[Recv] >>', ret)
        return ret

    def recvuntil(self, term='\n'):
        ret = b''
        while not ret.endswith(term.encode()):
            try:
                if self.mode == Mode.SOCKET:
                    ret += self.sock.recv(1)
                elif self.mode == Mode.LOCAL:
                    ret += self.proc.stdout.read(1)
            except self.timeout:
                if not ret.endswith(term.encode()):
                    log.warn(f'readuntil: not end with {repr(term)} (timeout)')
                break
            except Exception:
                sleep(0.05)
        if self.verbose:
            log.message(log.Color.DEEP_PURPLE, '[Recv] >>', ret)
        return ret

    def recvline(self):
        return self.recvuntil(term='\n')

    def interactive(self):
        from telnetlib import Telnet
        if self.verbose:
            log.info('Switching to interactive mode')
        
        go = threading.Event()
        def recv_thread():
            while not go.isSet():
                try:
                    cur = self.recv(4096, quiet=True)
                    stdout = sys.stdout
                    if cur:
                        stdout.write(cur.decode())
                        stdout.flush()
                except EOFError:
                    log.info('Got EOF while reading in interactive')
                    break
        t = threading.Thread(target=recv_thread)
        t.daemon = True
        t.start()

        try:
            while not go.isSet():
                stdin = sys.stdin
                data = stdin.readline()
                if data:
                    try:
                        self.send(data)
                    except EOFError:
                        go.set()
                        log.info('Got EOF while reading in interactive')
                else:
                    go.set()
        except KeyboardInterrupt:
            log.info('Interrupted')
            go.set()

        while t.is_alive():
            t.join(timeout=0.1)


    def PoW(self, hashtype, match, pts, begin=False, hx=False, length=20, start=b'', end=b''):
        import hashlib
        match = match.strip()
        x = b''
        rand_length = length - len(start) - len(end)
        if begin:
            log.proc(f'Searching x such that {hashtype}(x)[:{len(match.decode())}] == {match.decode()} ...')
            while (h := hashlib.new(hashtype, x).hexdigest()[:len(match)]) != match:
                x = start + random_string(rand_length, pts) + end

        else:
            log.proc(f'Searching x such that {hashtype}(x)[-{len(match.decode())}:] == {match.decode()} ...')
            while (h := hashlib.new(hashtype, x).hexdigest()[-(len(match)):]) != match:
                x = start + random_string(rand_length, pts) + end
    
        log.info(f"Found.  {hashtype}('{x.decode()}') == {h}")
        if hx:
            x = x.hex()
        self.sendline(x)


    def __del__(self):
        if self.mode == Mode.SOCKET:
            self.sock.close()
            if self.verbose:
                log.proc('Disconnected.')

        elif self.mode == Mode.LOCAL:
            if self.wait:
                self.proc.communicate(None)
            elif self.proc.poll() is None:
                self.proc.terminate()

            if self.verbose:
                log.proc(f'Stopped.')
        if self.pause:
            if self.verbose:
                log.info('Press any key to close.')
            input()

def urlencode(s, encoding='shift-jis', safe=':/&?='):
    from urllib.parse import quote_plus
    return quote_plus(s, encoding=encoding, safe=safe)

def urldecode(s, encoding='shift-jis'):
    from urllib.parse import unquote_plus
    return unquote_plus(s, encoding=encoding)

@singledispatch
def b64_padding(s):
    raise TypeError('s must be str or bytes.')

@b64_padding.register(str)
def b64_padding_str(s):
    s += '='*(-len(s)%4)
    return s

@b64_padding.register(bytes)
def b64_padding_bytes(s):
    s += b'='*(-len(s)%4)
    return s


def binary_to_image(data, padding=5, size=5, rev=False, image_size=(1000, 1000)):
    from PIL import Image, ImageDraw
    bk, wh = (0, 0, 0), (255, 255, 255)
    image = Image.new('RGB', image_size, wh)
    rect = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(rect)
    draw.rectangle((0, 0, size, size), fill=bk)

    h, w = 0, 0
    x, y = 0, 0
    for pixel in data:
        if pixel == '\n':
            y += 1
            h += 1
            w = max(w, x)
            x = 0
        else:
            if (pixel == '1') ^ rev:
                image.paste(rect, (padding+x*size, padding+y*size))
            x += 1

    return image.crop((0, 0, 2*padding+w*size, 2*padding+h*size))

    
# pwn
## utils
p8   = lambda x: pack('<B' if x > 0 else '<b', x)
p16  = lambda x: pack('<H' if x > 0 else '<h', x)
p32  = lambda x: pack('<I' if x > 0 else '<i', x)
p64  = lambda x: pack('<Q' if x > 0 else '<q', x)
u8   = lambda x, sign=False: unpack('<B' if not sign else '<b', x)[0] 
u16  = lambda x, sign=False: unpack('<H' if not sign else '<h', x)[0] 
u32  = lambda x, sign=False: unpack('<I' if not sign else '<i', x)[0] 
u64  = lambda x, sign=False: unpack('<Q' if not sign else '<q', x)[0] 
fill = lambda x, c='A', byte=True: (c*x).encode() if byte else c*x


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

def factorize(x):
    from factordb.factordb import FactorDB
    f = FactorDB(x)
    f.connect()
    return f.get_factor_list()

@singledispatch
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

@rot.register(str)
def rot_str(s, rotate=13):
    rotate %= 26
    r = ''
    for c in s:
        if 'A' <= c <= 'Z':
            r += chr((ord(c)-65+rotate)%26 + 65)
        elif 'a' <= c <= 'z':
            r += chr((ord(c)-97+rotate)%26 + 97)
        else:
            r += c
    return r


@rot.register(bytes)
def rot_bytes(s, rotate=13):
    rotate %= 26
    r = []
    for c in s:
        if 'A' <= chr(c) <= 'Z':
            r.append((c-65+rotate)%26 + 65)
        elif 'a' <= chr(c) <= 'z':
            r.append((c-97+rotate)%26 + 97)
        else:
            r.append(c)
    return bytes(r)


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
    return pow(e, -1, (p-1)*(q-1))

def chinese_remainder(a, p):
    assert len(a) == len(p)
    P = reduce(lambda x, y: x*y, p)
    x = sum([ai * pow(P//pi, -1, pi) * P // pi for ai, pi in zip(a, p)])
    return x % P


## Vigenere
def vigenere(cipher, key):
    pts = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    key = key.lower()
    key = [ord('a') - ord(c) for c in key]
    ans = ''
    i = 0
    for c in cipher:
        if not c in pts:
            ans += c
        else:
            ans += rot(c, key[i % len(key)])
            i += 1
    return ''.join(ans)


## Common Modulus Attack
def common_modulus_attack(e1, e2, c1, c2, n):
    s1, s2, _ = extended_gcd(e1, e2)
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


def baby_giant(g, y, p, q=None):
    if not q:
        q = p
    m = ceil(gmpy2.isqrt(q))
    table = {}
    b = 1
    for i in range(m):
        table[b] = i
        b = (b*g) % p

    gim = pow(pow(g, -1, p), m, p)
    gmm = y

    for i in range(m):
        if gmm in table.keys():
            return int(i*m + table[gmm])
        else:
            gmm *= gim
            gmm %= p

    return -1


def pohlig_hellman(g, y, p):
    phi_p = factorize(p-1)
    X = [baby_giant(pow(g, (p-1)//q, p), pow(y, (p-1)//q, p), p, q)
         for q in phi_p]

    x = chinese_remainder(X, phi_p)
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

def lsb_decryption_oracle_attack(n, e, c, oracle, progress=True):
    """
    oracle: method 
        decryption oracle
        c*2**e = (2*m)**e (mod n) >> oracle >> m&1
    """
    from fractions import Fraction

    l, r = 0, n
    C = c
    i = 0
    nl = n.bit_length()
    while r-l > 1:
        if progress:
            log.proc(f'{(100*i//nl):>3}% [{i:>4}/{nl}]')

        mid = Fraction(l+r, 2)
        C = C*pow(2, e, n) % n
        if oracle(C):
            l = mid
        else:
            r = mid
        i += 1
        

    return int(ceil(l))

# |chosen_pt|FLAG|pad|
def ecb_chosen_plaintext_attack(encrypt_oracle, plaintext_space=b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789{}_', known_plaintext=b'', block_size=16, verbose=False):
    from random import sample
    block_end = block_size * (len(known_plaintext)//(block_size-2) + 1)
    for _ in range(1, 100):

        # shuffle plaintext_space to reduce complexity
        plaintext_space = bytes(sample(bytearray(plaintext_space), len(plaintext_space)))

        # get the encrypted block which includes the beginning of FLAG
        if verbose:
            log.info('Getting the encrypted block which includes the beginning of FLAG')

        if len(known_plaintext) % block_size == block_size-1:
            block_end += block_size

        
        chosen_plaintext = b'\x00'*(block_end-len(known_plaintext)-1) 
        print(chosen_plaintext)
        encrypted_block = encrypt_oracle(chosen_plaintext)
        encrypted_block = encrypted_block[block_end-block_size:block_end]


        # bruteforcing all of the characters in plaintext_space 
        if verbose:
            log.info('Bruteforcing all of the characters in plaintext_space')
        for c in plaintext_space:
            if verbose:
                sys.stderr.write(f'\r{log.colorify(log.Color.GREY, known_plaintext[:-1].decode())}{log.colorify(log.Color.RED, known_plaintext[-1:].decode())}{log.colorify(log.Color.MAGENTA, chr(c))}')
            payload = b'\x00'*(block_end-len(known_plaintext)-1) + known_plaintext + bytearray([c])
            enc_block = encrypt_oracle(payload)[block_end-block_size:block_end]
            if encrypted_block == enc_block:
                known_plaintext += bytearray([c])
                if verbose:
                    sys.stderr.write('\n')
                break



# [str,b64encoded] plaintext >> padding_oracle >> [bool] padding is valid?
def padding_oracle_attack(ciphertext, padding_oracle, iv=b'', block_size=16, verbose=False):
    from base64 import b64encode
    cipher_block = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    cipher_block.reverse()
    plaintext = b''

    def is_valid(c_target, d_prev, nth_byte, i):
        attempt_byte = bytes.fromhex(f'{i:02x}')
        adjusted_bytes = bytes(c^nth_byte for c in d_prev)

        payload = b'\x00'*(block_size-nth_byte) + attempt_byte + adjusted_bytes + c_target
        if verbose:
            sys.stdout.write('\033[2K\033[G'
                    +log.colorify(log.Color.GREY, repr(b'\x00'*(block_size-nth_byte))[2:-1]) 
                    +log.colorify(log.Color.RED, repr(attempt_byte)[2:-1])
                    +log.colorify(log.Color.MAGENTA, repr(adjusted_bytes)[2:-1])
                    +log.colorify(log.Color.DARK_GREY, repr(c_target)[2:-1])
            )
            sys.stdout.flush()

        payload = b64encode(payload).decode()
        return padding_oracle(payload)


    for _ in range(len(cipher_block)-1):
        c_target, c_prev = cipher_block[:2]
        print(cipher_block)
        cipher_block.pop(0)
        nth_byte = 1
        i = 0
        m = d_prev = b''
        while True:
            if is_valid(c_target, d_prev, nth_byte, i):
                m += bytes.fromhex(f'{i^nth_byte^c_prev[-nth_byte]:02x}')
                d_prev = bytes.fromhex(f'{i^nth_byte:02x}')+d_prev
                nth_byte += 1
                i = 0
                if nth_byte <= block_size:
                    continue
                break
            i += 1
            if i > 0xff:
                log.error('Not Found')
                return None
        plaintext = m[::-1] + plaintext 

        if verbose:
            print()
            log.info(f'Decrypt(c{len(cipher_block)}): {repr(d_prev)[2:-1]}')
            log.info(f'm{len(cipher_block)}: {repr(m[::-1])[2:-1]}')
            log.info(f'plaintext: {repr(plaintext)[2:-1]}')

    return plaintext



def session_falsification(data, secret_key):
    import flask.sessions
    class App:
        def __init__(self, secret_key):
            self.secret_key = secret_key

    app = App(secret_key)
    si = flask.sessions.SecureCookieSessionInterface()
    s = si.get_signing_serializer(app)
    data = s.dumps(data)
    return data



def lcg_crack(X, A=None, B=None, M=None):
    if A and B:
        M = gcd(X[2]-A*X[1]-B, X[1]-A*X[0]-B)

    Y = [X[i+1]-X[i] for i in range(len(X)-1)]
    print(Y)
    Z = [Y[i]*Y[i+3] - Y[i+1]*Y[i+2] for i in range(len(X)-4)]
    M = reduce(gcd, Z)

    if M and len(X) >= 3:
        A = (X[2]-X[1]) * pow(X[1]-X[0], -1, M) % M

    if A and M and len(X) >= 2:
        B = (X[1]-A*X[0]) % M

    assert [(A*X[i]+B)%M == X[i+1] for i in range(len(X)-1)]

    return A, B, M
    
    

# Attack and Defense
@singledispatch
def submit_flag(flags, url, token):
    raise TypeError('flag must be str or list.')


@submit_flag.register(list)
def submit_flag_list(flags, url, token):
    header = {
        'x-api-key': token,
    }
    for flag in flags:
        data = {
            'flag': flag,
        }
        response = requests.post(url, data={'flag': flag}, headers=header)
        log.info(response.text)

@submit_flag.register(str)
def submit_flag_str(flag, url, token):
    header = {
        'x-api-key': token,
    }
    data = {
        'flag': flag,
    }
    response = requests.post(url, data={'flag': flag}, headers=header)
    log.info(response.text)







