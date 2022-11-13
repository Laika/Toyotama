import ast
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
    def recv(self, n: int = 4096, debug: bool = False):
        ...

    def recvuntil(self, term: bytes) -> bytes:
        buf = b""
        if isinstance(term, str):
            term = term.encode()

        while not buf.endswith(term):
            buf += self.recv(1, debug=False)

        logger.info(f"[> {buf!r}")

        return buf

    def recvlines(self, repeat: int) -> bytes:
        return [self.recvline() for _ in range(repeat)]

    def recvline(self) -> bytes:
        return self.recvuntil(term=b"\n")

    def recvlineafter(self, term: bytes) -> bytes | list[bytes]:
        self.recvuntil(term)
        return self.recvline()

    def recvvalue(self, parser: Callable = lambda x: ast.literal_eval(x)):
        pattern_raw = r"(?P<name>.*) *[=:] *(?P<value>.*)"
        pattern = re.compile(pattern_raw)
        line = pattern.match(self.recvline().decode())
        name = line.group("name").strip()
        value = parser(line.group("value"))

        logger.debug(f"{name}: {value}")

        return value

    def recvint(self) -> int:
        return self.recvvalue(parser=lambda x: int(x, 0))

    @abstractmethod
    def send(self, message: bytes | str | int, term: bytes = b""):
        ...

    def sendline(self, message: bytes | int):
        self.send(message, term=b"\n")

    def sendlineafter(self, term: bytes, msg: bytes | int):
        data = self.recvuntil(term)
        self.sendline(msg)
        return data

    def interactive(self):
        logger.info("Switching to interactive mode.")

        go = threading.Event()

        def recv_thread():
            while not go.is_set():
                try:
                    buf = self.recv(debug=False)
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
            while not go.is_set():
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
