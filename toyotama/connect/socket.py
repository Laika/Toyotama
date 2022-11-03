import socket

from ..util.log import get_logger
from .tube import Tube

logger = get_logger()


class Socket(Tube):
    def __init__(self, target: str, timeout: float = 20.0):
        super().__init__()
        _, host, port = target.split()
        self.host: str = host
        self.port: int = int(port)
        self.timeout: float = timeout
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(timeout)
        self.sock.connect((self.host, self.port))

    def _socket(self):
        return self.sock

    def recv(self, n: int = 4096, debug: bool = True):
        try:
            buf = self.sock.recv(n)
        except Exception as e:
            logger.error(e)

        if debug:
            logger.debug(f"[> {buf!r}")

        return buf

    def send(self, message: bytes | int | str, term_char: bytes | str = b""):
        msg: bytes = b""
        term: bytes = b""

        if isinstance(term_char, str):
            term = term_char.encode()

        if isinstance(msg, int):
            msg += str(msg).encode()
        if isinstance(msg, str):
            msg += msg.encode()

        msg += term

        try:
            self.sock.sendall(msg)
            logger.debug(f"<] {msg!r}")
        except Exception as e:
            self.is_alive = False
            logger.error(e)

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            logger.info(f"Connection to {self.host}:{self.port} closed.")
