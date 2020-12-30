import fcntl
import os
import socket
import subprocess
import sys
import threading
from enum import Enum
from string import printable
from time import sleep

from toyotama.util.log import Color, info, message, proc, warn


class Mode(Enum):
    SOCKET = 1
    LOCAL = 2


class Connect:
    def __init__(
        self, target, mode=Mode.SOCKET, to=10.0, verbose=True, pause=True, raw_output=True, **args
    ):
        if mode not in Mode:
            warn(f"Connect: {mode} is not defined.")
            info("Connect: Automatically set to 'SOCKET'.")
        self.mode = mode
        self.verbose = verbose
        self.pause = pause
        self.raw_output = raw_output
        self.is_alive = True

        if target.startswith("./"):
            target = {"program": target}
        elif target.startswith("nc"):
            _, host, port = target.split()
            target = {"host": host, "port": int(port)}

        if self.mode == Mode.SOCKET:
            host, port = target["host"], target["port"]
            if self.verbose:
                proc(f"Connecting to {host}:{port}...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(to)
            self.sock.connect((host, port))
            self.timeout = socket.timeout

        if self.mode == Mode.LOCAL:
            program = target["program"]
            self.wait = "wait" in args and args["wait"]
            if self.verbose:
                proc(f"Starting {program} ...")
            self.proc = subprocess.Popen(
                program,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if self.verbose:
                info(f"PID: {self.proc.pid}")
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
                try:
                    if self.raw_output:
                        message(Color.BLUE, "[Send] <<", msg)
                    else:
                        message(Color.BLUE, "[Send] <<", msg.decode())
                except Exception:
                    message(Color.BLUE, "[Send] <<", msg)
        except Exception:
            self.is_alive = False

    def sendline(self, message):
        if isinstance(message, str):
            self.send(message + "\n")
        else:
            self.send(message + b"\n")

    def recv(self, n=2048, quiet=False):
        sleep(0.05)
        ret = b""
        try:
            if self.mode == Mode.SOCKET:
                ret = self.sock.recv(n)
            elif self.mode == Mode.LOCAL:
                ret = self.proc.stdout.read(n)
        except Exception:
            pass

        if not quiet and self.verbose:
            try:
                if self.raw_output:
                    message(Color.DEEP_PURPLE, "[Recv] >>", ret)
                else:
                    message(Color.DEEP_PURPLE, "[Recv] >>", ret.decode())
            except Exception:
                message(Color.DEEP_PURPLE, "[Recv] >>", ret)
        return ret

    def recvuntil(self, term="\n"):
        ret = b""
        while not ret.endswith(term.encode()):
            try:
                if self.mode == Mode.SOCKET:
                    ret += self.sock.recv(1)
                if self.mode == Mode.LOCAL:
                    print(self.proc.stdout)
                    ret += self.proc.stdout.read(1)
            except self.timeout:
                if not ret.endswith(term.encode()):
                    warn(f"recvuntil: Not ends with {repr(term)} (Timeout)")
                break
            except Exception:
                sleep(0.05)
        if self.verbose:
            try:
                if self.raw_output:
                    message(Color.DEEP_PURPLE, "[Recv] >>", ret)
                else:
                    message(Color.DEEP_PURPLE, "[Recv] >>", ret.decode())
            except Exception:
                message(Color.DEEP_PURPLE, "[Recv] >>", ret)

        return ret

    def recvline(self, repeat=1):
        buffer = [self.recvuntil(term="\n") for i in range(repeat)]
        return buffer.pop() if len(buffer) == 1 else buffer

    def interactive(self):
        if self.verbose:
            info("Switching to interactive mode")

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
                    info("Got EOF while reading in interactive")
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
                        info("Got EOF while reading in interactive")
                else:
                    go.set()
        except KeyboardInterrupt:
            info("Interrupted")
            go.set()

        while t.is_alive():
            t.join(timeout=0.1)

    def PoW(
        self, hashtype, match, pts=printable, begin=False, hx=False, length=20, start=b"", end=b""
    ):
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
            proc(f"Searching x such that {hashtype}({start} x {end})[:{len(match)}] == {match} ...")
            for patt in product(pts, repeat=rand_length):
                patt = start + bytes(patt) + end
                h = hashlib.new(hashtype, patt).hexdigest()[: len(match)]
                if h == match:
                    break
        else:
            proc(
                f"Searching x such that {hashtype}({start} x {end})[-{len(match)}:] == {match} ..."
            )
            for patt in product(pts, repeat=rand_length):
                patt = start + bytes(patt) + end
                h = hashlib.new(hashtype, patt).hexdigest()[-len(match) :]
                if h == match:
                    break

        info(f"Found.  {hashtype}('{patt.decode()}') == {h}")
        if hx:
            patt = patt.hex()
        self.sendline(patt)

    def __del__(self):
        if self.mode == Mode.SOCKET:
            self.sock.close()
            if self.verbose:
                proc("Disconnected.")

        elif self.mode == Mode.LOCAL:
            if self.wait:
                self.proc.communicate(None)
            elif self.proc.poll() is None:
                self.proc.terminate()

            if self.verbose:
                proc("Stopped.")
        if self.pause:
            if self.verbose:
                info("Press any key to close.")
            input()
