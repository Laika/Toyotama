import socket

from ..util.log import get_logger
from .tube import Tube

logger = get_logger()


class Socket(Tube):
    def __init__(self, target: str, timeout: float = 20.0):
        super().__init__()
        _, host, port = target.split()
        self.host = host
        self.port = int(port)
        self.timeout = timeout
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(timeout)
        self.sock.connect((self.host, self.port))
        self.timeout = socket.timeout

    def _socket(self):
        return self.sock

    def recv(self, n: int = 4096, quiet: bool = False):
        try:
            buf = self.sock.recv(n)
        except Exception as e:
            logger.error(e)

        if not quiet:
            logger.info(f"[> {buf}")

        return buf

    def send(self, msg: bytes | int | str, term: bytes | int | str):
        if isinstance(msg, int):
            msg = str(msg).encode()
        if isinstance(msg, str):
            msg = msg.encode()

        msg += term

        try:
            self.sock.sendall(msg)
            logger.info(f"<] {msg}")
        except Exception as e:
            self.is_alive = False
            logger.error(e)

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            logger.info(f"Connection to {self.host}:{self.port} closed.")
