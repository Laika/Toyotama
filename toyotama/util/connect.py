import fcntl
import os
import re
import socket
import subprocess
import sys
import threading
from enum import IntEnum
from string import printable
from time import sleep

from toyotama.util.log import get_logger

logger = get_logger(__name__)


class Mode(IntEnum):
    SOCKET = 1
    LOCAL = 2


class Connect:
    def __init__(self, target, mode=Mode.SOCKET, timeout=20.0, verbose=True, pause=True, raw_output=True, **args):
        self.mode = mode
        if mode not in Mode:
            logger.warning(f"Connect: {mode} is not defined.")
            logger.info("Connect: Automatically set to 'SOCKET'.")
            self.mode = Mode.SOCKET
        self.verbose = verbose
        self.pause = pause
        self.raw_output = raw_output
        self.is_alive = True

        if target.startswith("./"):
            target = {"program": target}
        elif target.startswith("nc"):
            _, host, port = target.split()
            target = {"host": host, "port": int(port)}

        match self.mode:
            case Mode.SOCKET:
                host, port = target["host"], target["port"]
                if self.verbose:
                    logger.info(f"Connecting to {host!s}:{port}...")
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(timeout)
                self.sock.connect((str(host), port))
                self.timeout = socket.timeout

            case Mode.LOCAL:
                program = target["program"]
                self.wait = "wait" in args and args["wait"]
                if self.verbose:
                    logger.info(f"Starting {program} ...")
                self.proc = subprocess.Popen(
                    program,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                if self.verbose:
                    logger.info(f"PID: {self.proc.pid}")
                self.set_nonblocking(self.proc.stdout)
                self.timeout = None

    def set_nonblocking(self, fh):
        fd = fh.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    def send(self, msg, end=b""):
        if isinstance(msg, int):
            msg = str(msg).encode()
        if isinstance(msg, str):
            msg = msg.encode()

        msg += end

        try:
            match self.mode:
                case Mode.SOCKET:
                    self.sock.sendall(msg)
                case Mode.LOCAL:
                    self.proc.stdin.write(msg)

            if self.verbose:
                try:
                    if self.raw_output:
                        logger.info(f"<] {msg}")
                    else:
                        logger.info(f"<] {msg.decode()}")
                except Exception:
                    logger.info(f"<] {msg}")
        except Exception:
            self.is_alive = False

    def sendline(self, message):
        self.send(message, end=b"\n")

    def sendafter(self, term, message, end=b""):
        self.recvuntil(term=term)
        self.send(message, end=end)

    def sendlineafter(self, term, message):
        self.sendafter(term, message, end=b"\n")

    def recv(self, n=2048, quiet=False):
        sleep(0.05)
        ret = b""
        try:
            match self.mode:
                case Mode.SOCKET:
                    ret = self.sock.recv(n)
                case Mode.LOCAL:
                    ret = self.proc.stdout.read(n)
        except Exception as e:
            logger.warning(e)

        if not quiet and self.verbose:
            try:
                if self.raw_output:
                    logger.info(f"[> {ret}")
                else:
                    logger.info(f"[> {ret.decode()}")
            except Exception:
                logger.info(f"[> {ret}")
        return ret

    def recvuntil(self, term=b"\n") -> bytes:
        ret = b""
        if isinstance(term, str):
            term = term.encode()
        while not ret.endswith(term):
            try:
                match self.mode:
                    case Mode.SOCKET:
                        ret += self.sock.recv(1)
                    case Mode.LOCAL:
                        ret += self.proc.stdout.read(1)
            except self.timeout:
                if not ret.endswith(term):
                    logger.warning(f"recvuntil: Not ends with {term!r} (Timeout)")
                break
            except Exception:
                sleep(0.05)
        if self.verbose:
            try:
                if self.raw_output:
                    logger.info(f"[> {ret}")
                else:
                    logger.info(f"[> {ret.decode()}")
            except Exception:
                logger.info(f"[> {ret}")

        return ret

    def recvline(self, repeat=1) -> bytes | list[bytes]:
        buf = [self.recvuntil(term=b"\n") for i in range(repeat)]
        return buf.pop() if len(buf) == 1 else buf

    def recvvalue(self, parse=lambda x: x):
        pattern = r"(?P<name>.*) *[=:] *(?P<value>.*)"
        pattern = re.compile(pattern)
        line = pattern.match(self.recvline().decode())
        name = line.group("name").strip()
        value = parse(line.group("value"))

        if self.verbose:
            logger.info(f"{name}: {value}")
        return value

    def recvint(self) -> int:
        return self.recvvalue(parse=lambda x: int(x, 0))

    def interactive(self):
        if self.verbose:
            logger.info("Switching to interactive mode")

        go = threading.Event()

        def recv_thread():
            while not go.isSet():
                try:
                    cur = self.recv(4096, quiet=True)
                    stdout = sys.stdout
                    if cur:
                        stdout.buffer.write(cur)
                        stdout.flush()
                except EOFError:
                    logger.info("Got EOF while reading in interactive")
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
                        logger.info("Got EOF while reading in interactive")
                else:
                    go.set()
        except KeyboardInterrupt:
            logger.info("Interrupted")
            go.set()

        while t.is_alive():
            t.join(timeout=0.1)

    def PoW(self, hashtype, match, pts=printable, begin=False, hex=False, length=20, start=b"", end=b""):
        import hashlib
        from itertools import product

        if isinstance(hashtype, bytes):
            hashtype = hashtype.decode()
        if isinstance(match, bytes):
            match = match.decode()

        hashtype = hashtype.strip()
        match = match.strip()
        pts = pts.encode()

        rand_length = length - len(start) - len(end)

        if begin:
            logger.info(f"Searching x such that {hashtype}({start} x {end})[:{len(match)}] == {match} ...")
            for patt in product(pts, repeat=rand_length):
                patt = start + bytes(patt) + end
                h = hashlib.new(hashtype, patt).hexdigest()[: len(match)]
                if h == match:
                    break
        else:
            logger.info(f"Searching x such that {hashtype}({start} x {end})[-{len(match)}:] == {match} ...")
            for patt in product(pts, repeat=rand_length):
                patt = start + bytes(patt) + end
                h = hashlib.new(hashtype, patt).hexdigest()[-len(match) :]
                if h == match:
                    break

        logger.inf(f"Found.  {hashtype}('{patt.decode()}') == {h}")
        if hex:
            patt = patt.hex()
        self.sendline(patt)

    def __del__(self):
        match self.mode:
            case Mode.SOCKET:
                self.sock.close()
                if self.verbose:
                    logger.info("Disconnected.")

            case Mode.LOCAL:
                if self.wait:
                    self.proc.communicate(None)
                elif self.proc.poll() is None:
                    self.proc.terminate()

        if self.verbose:
            logger.info("Stopped.")
        if self.pause:
            if self.verbose:
                logger.info("Press any key to close.")
            input()
