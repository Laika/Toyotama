import re
import sys
import threading
import time
from abc import ABCMeta, abstractmethod
from typing import Callable

from ..terminal.style import Style
from ..util.log import get_logger

logger = get_logger()


class Tube(metaclass=ABCMeta):
    def __init__(self):
        ...

    @abstractmethod
    def recv(self, n: int = 4096, quiet: bool = False):
        ...

    def recvuntil(self, term: bytes | str) -> bytes | str:
        buf = b""
        if isinstance(term, str):
            term = term.encode()

        while not buf.endswith(term):
            buf += self.recv(1, quiet=True)

        logger.info(f"[> {buf}")

        return buf

    def recvline(self, repeat: int = 1) -> bytes | str:
        buf = [self.recvuntil(term=b"\n") for _ in range(repeat)]
        return buf.pop() if len(buf) == 1 else buf

    def recvlineafter(self, term: bytes | str) -> bytes | str:
        self.recvuntil(term)
        return self.recvline()

    def recvvalue(self, parse: Callable = lambda x: x):
        pattern = r"(?P<name>.*) *[=:] *(?P<value>.*)"
        pattern = re.compile(pattern)
        line = pattern.match(self.recvline().decode())
        name = line.group("name").strip()
        value = parse(line.group("value"))

        logger.info(f"{name}: {value}")

        return value

    def recvint(self) -> int:
        return self.recvvalue(parse=lambda x: int(x, 0))

    @abstractmethod
    def send(self, msg: int | str | bytes, term: str | bytes = b""):
        ...

    def sendline(self, msg: bytes | int | str):
        self.send(msg, end=b"\n")

    def sendlineafter(self, term: bytes | str, msg: bytes | int | str):
        data = self.recvuntil(term)
        self.sendline(msg, end=b"\n")
        return data

    def interactive(self):
        logger.info("Switching to interactive mode.")

        go = threading.Event()

        def recv_thread():
            while not go.isSet():
                try:
                    buf = self.recv(quiet=True)
                    if buf:
                        sys.stdout.write(buf.decode())
                        sys.stdout.flush()
                except EOFError:
                    logger.error("Got EOF while reading in interactive")
                    break

        t = threading.Thread(target=recv_thread)
        t.daemon = True
        t.start()

        try:
            while not go.isSet():
                sys.stdout.write(f"{Style.FG_VIOLET}>{Style.RESET} ")
                sys.stdout.flush()
                data = sys.stdin.readline()
                if data:
                    try:
                        self.send(data)
                    except EOFError:
                        go.set()
                        logger.error("Got EOF while reading in interactive.")
                else:
                    go.set()
                time.sleep(0.05)
        except KeyboardInterrupt:
            logger.warning("Interrupted")
            go.set()

        while t.is_alive():
            t.join(timeout=0.1)

    def __enter__(self):
        return self

    def __exit__(self, e_type, e_value, traceback):
        self.close()

    @abstractmethod
    def close(self):
        ...
