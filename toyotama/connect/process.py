import fcntl
import os
import pty
import signal
import subprocess
import tty
from pathlib import Path

from ..util.log import get_logger
from .tube import Tube

logger = get_logger()


class Process(Tube):
    def __init__(self, args: list[str], env: dict[str, str] | None = None):
        super().__init__()
        self.path: Path = Path(args[0])
        self.args: list[str] = args
        self.env: dict[str, str] | None = env
        self.proc: subprocess.Popen | None
        self.returncode: int | None = None

        master, slave = pty.openpty()
        tty.setraw(master)
        tty.setraw(slave)

        try:
            self.proc = subprocess.Popen(
                self.args,
                env=self.env,
                shell=False,
                stdin=subprocess.PIPE,
                stdout=slave,
                stderr=subprocess.STDOUT,
            )
        except Exception as e:
            logger.error(e)

        if self.proc is None:
            logger.error("Failed to create a new process")
            return

        if master:
            self.proc.stdout = os.fdopen(os.dup(master), "r+b", 0)
            os.close(master)

        fd = self.proc.stdout.fileno()
        fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)

        logger.info(f"Created a new process (PID: {self.proc.pid})")

    def _socket(self) -> subprocess.Popen | None:
        return self.proc

    def pid(self) -> int:
        return getattr(self.proc, "pid", -1)

    def _poll(self) -> int | None:
        if self.proc is None:
            return None
        self.proc.poll()
        if self.proc.returncode and self.returncode is None:
            self.returncode = -self.proc.returncode
            logger.error(f"{self.path!s} terminated: {signal.strsignal(self.returncode)} (PID={self.proc.pid})")

        return self.returncode

    def is_alive(self):
        return self._poll() is None

    def is_dead(self):
        return not self.is_alive()

    def recv(self, n: int = 4096, debug: bool = True) -> bytes:
        if self.is_dead():
            return b""

        if self.proc.stdout is None:
            return b""
        try:
            buf = self.proc.stdout.read(n)
            if buf:
                self.recv_bytes += len(buf)
        except Exception as e:
            logger.error(e)
            return b""

        if debug:
            logger.debug(f"[> {buf!r}")

        self._poll()

        return buf or b""

    def send(self, message: bytes | str | int, term: bytes | str = b"", debug: bool = True):
        if self.is_dead():
            return b""

        self._poll()
        payload = b""
        if isinstance(message, str):
            payload += message.encode()
        if isinstance(message, int):
            payload += str(message).encode()

        if isinstance(term, str):
            term = term.encode()

        payload += term

        try:
            self.proc.stdin.write(payload)
            self.send_bytes += len(payload)
            self.proc.stdin.flush()
            if debug:
                logger.debug(f"<] {payload!r}")
        except OSError:
            logger.warning("Broken pipe")
        except Exception as e:
            logger.error(e)

    def gdb(self, script: list[str] | None = None):
        self._gdb = subprocess.Popen(["gdb", "-p", str(self.pid())], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        master, slave = pty.openpty()
        tty.setraw(master)
        tty.setraw(slave)

    def close(self):
        if self.proc is None:
            return

        self.proc.kill()
        self.proc.wait()

        logger.info(f"{self.path!s} killed (PID={self.proc.pid})")

        self.proc = None

    def __del__(self):
        self.close()
