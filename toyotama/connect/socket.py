import socket

from ..util.log import get_logger
from .tube import Tube

logger = get_logger()


class Socket(Tube):
    def __init__(self, target: str, timeout: float = 30.0):
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
        buf = b""
        try:
            buf += self.sock.recv(n)
        except Exception as e:
            logger.error(e)

        if debug:
            logger.debug(f"[> {buf!r}")

        return buf

    def send(self, message: bytes | int | str, term: bytes = b""):
        payload = b""

        if isinstance(term, str):
            term = term.encode()

        if isinstance(message, int):
            payload += str(message).encode()
        if isinstance(message, str):
            payload += message.encode()

        payload += term

        try:
            self.sock.sendall(payload)
            logger.debug(f"<] {payload!r}")
        except Exception as e:
            self.is_alive = False
            logger.error(e)

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            logger.info(f"Connection to {self.host}:{self.port} closed.")
