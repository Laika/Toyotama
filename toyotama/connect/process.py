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
    def __init__(self, args: list[str], env: list[str] = None):
        super().__init__()
        self.path = Path(args[0])
        self.args = args
        self.env = env
        self.proc = None
        self.returncode = None

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

        if master:
            self.proc.stdout = os.fdopen(os.dup(master), "r+b", 0)
            os.close(master)

        fd = self.proc.stdout.fileno()
        fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)

        logger.info(f"Created a new process (PID: {self.proc.pid})")

    def _socket(self):
        return self.proc

    def _poll(self):
        self.proc.poll()
        if self.proc.returncode and self.returncode is None:
            self.returncode = self.proc.returncode
            logger.error(f"{self.path!s} terminated: {signal.strsignal(-self.returncode)} (PID={self.proc.pid})")

        return self.returncode

    def _is_alive(self):
        return self._poll() is None

    def recv(self, n=4096, quiet=False) -> bytes:
        try:
            buf = self.proc.stdout.read(n)
        except Exception as e:
            logger.error(e)
            return None

        if not quiet:
            logger.info(f"[> {buf}")

        self._poll()

        return buf

    def send(self, msg: bytes | int | str):
        self._poll()
        if isinstance(msg, str):
            msg = msg.encode()
        if isinstance(msg, int):
            msg = str(msg).encode()

        try:
            self.proc.stdin.write(msg)
            self.proc.stdin.flush()
        except IOError:
            logger.warning("Broken pipe")
        except Exception as e:
            logger.error(e)

    def close(self):
        if self.proc is None:
            return

        self.proc.kill()
        self.proc.wait()

        logger.info(f"{self.path!s} killed (PID={self.proc.pid})")

        self.proc = None

    def __del__(self):
        self.close()
