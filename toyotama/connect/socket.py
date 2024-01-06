import os
import socket
import subprocess

from toyotama.connect.tube import Tube
from toyotama.util.log import get_logger

logger = get_logger(__name__, os.environ.get("TOYOTAMA_LOG_LEVEL", "INFO"))


class Socket(Tube):
    def __init__(self, target: str, timeout: float = 30.0):
        """Create a socket connection to a remote host.

        Args:
        target (str): The target host and port. Example: "nc localhost 1234"
        timeout (float, optional): Timeout in seconds. Defaults to 30.0.
        """

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

    def recv(self, n: int = 4096) -> bytes:
        if self.sock is None:
            return b""
        buf = b""
        try:
            buf += self.sock.recv(n)
        except Exception as e:
            logger.error(e)

        self.recv_bytes += len(buf)

        return buf

    def send(self, message: bytes | str | int, term: bytes | str = b""):
        if self.sock is None:
            return

        payload = b""

        message = self._to_bytes(message)
        payload += message

        term = self._to_bytes(term)
        payload += term

        self.send_bytes += len(payload)

        try:
            self.sock.sendall(payload)
        except Exception as e:
            self.is_alive = False
            logger.error(e)

    def solve_hashcash(self, command: str) -> str:
        commands = command.strip().split()
        if commands[0] != "hashcash":
            raise ValueError("Invalid hashcash command.")

        result = subprocess.run(commands, capture_output=True).stdout.decode().strip()
        self.sendline(result)

        return result

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            logger.info(f"Connection to {self.host}:{self.port} closed.")


__all__ = ["Socket"]
