import fcntl
import socket
import threading
from toyotama.util.log import *
from enum import Enum

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

