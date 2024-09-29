import errno
import fcntl
import os
import pty
import select
import signal
import subprocess
import tty
from logging import getLogger
from pathlib import Path

from libtmux import Server  # pyright: ignore
from libtmux.constants import PaneDirection

from toyotama.connect.tube import Tube

logger = getLogger(__name__)


class Process(Tube):
    def __init__(
        self,
        path: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        timeout: float | None = None,
    ):
        super().__init__()
        self.path: Path = Path(path)
        self.args: list[str] = args or []
        self.env: dict[str, str] = env or {}
        self.proc: subprocess.Popen | None
        self.returncode: int | None = None
        self.timeout: float | None = timeout

        master, slave = pty.openpty()
        tty.setraw(master)
        tty.setraw(slave)

        try:
            self.proc = subprocess.Popen(
                [path] + self.args,
                env=self.env,
                shell=False,
                stdin=subprocess.PIPE,
                stdout=slave,
                stderr=subprocess.STDOUT,
            )
        except FileNotFoundError:
            logger.error('File not found: "%s"', path)
            return
        except Exception as e:
            logger.error("Process.__init__(): %s", e)
            return

        if master:
            self.proc.stdout = os.fdopen(os.dup(master), "r+b", 0)
            os.close(master)

        if not hasattr(self.proc, "stdout"):
            logger.error("Process.__init__(): Failed to open a pipe")
            return

        fd = self.proc.stdout.fileno()  # pyright: ignore
        fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)

        logger.info("Created a new process (PID: %d)", self.proc.pid)

    def _socket(self) -> subprocess.Popen | None:
        return self.proc

    def pid(self) -> int:
        return getattr(self.proc, "pid", -1)

    def _poll(self) -> int | None:
        if self.proc is None:
            return None
        self.proc.poll()
        returncode = self.proc.returncode
        if returncode is not None and self.returncode is None:
            self.returncode = returncode

            logger.error('"%s" terminated: %s (PID=%d)', str(self.path), signal.strsignal(-self.returncode), self.proc.pid)

        return returncode

    def is_alive(self):
        return self._poll() is None

    def is_dead(self):
        return not self.is_alive()

    def is_ready(self) -> bool:
        if self.proc is None:
            return False

        try:
            ready = select.select([self.proc.stdout], [], [], self.timeout)
            if ready == ([], [], []):
                raise TimeoutError(f"Process.is_ready(): timeout {self.timeout}s")
        except TimeoutError as e:
            raise e from None
        except OSError as e:
            if e.errno == errno.EINTR:
                return True

        return True

    def recv(self, n: int = 4096) -> bytes:
        if not self.is_ready():
            logger.warning("Process.recv(): not ready")
            return b""

        if self.is_dead():
            logger.warning("Process.recv(): process is dead")
            return b""

        if self.proc.stdout is None:  # pyright: ignore
            logger.warning("Process.recv(): stdout is None")
            return b""

        buf = b""
        try:
            buf += self.proc.stdout.read(n) or b""  # pyright: ignore
        except Exception as e:
            logger.error("%s", e)
            input()

        self.recv_bytes += len(buf)

        self._poll()

        return buf

    def send(self, message: bytes | str | int, term: bytes | str = b""):
        self._poll()

        payload = b""

        message = self._to_bytes(message)
        payload += message

        term = self._to_bytes(term)
        payload += term

        self.send_bytes += len(payload)

        try:
            self.proc.stdin.write(payload)  # pyright: ignore
            self.proc.stdin.flush()  # pyright: ignore
        except OSError:
            logger.warning("Broken pipe")
        except Exception as e:
            logger.error("Process.send(): %s", e)

    def gdb(self, script: str = "", host: str = "localhost", port: int = 51280):
        self._gdbserver = subprocess.Popen(
            ["gdbserver", f"{host}:{port}", "--attach", str(self.pid())],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
        )
        logger.info("gdbserver started (PID: %d)", self._gdbserver.pid)

        # tmux
        srv = Server()
        session = srv.sessions[0]

        try:
            pane = session.active_window.active_pane.split(direction=PaneDirection.Right, shell="gdb")

            pane.send_keys(f"file {self.path!s}")
            pane.send_keys(f"target extend-remote {host}:{port}")
            for line in script.split(os.linesep):
                pane.send_keys(line)

        except Exception as e:
            logger.error("Process.gdb(): %s", e)

    def close(self):
        if self.proc is None:
            return

        if self.is_alive():
            logger.info('"%s" killed (PID=%d)', self.path, self.proc.pid)
            self.proc.stdin.close()  # pyright: ignore
            self.proc.stdout.close()  # pyright: ignore
            self.proc.kill()
            self.proc.wait()

        self.proc = None

    def __del__(self):
        self.close()
