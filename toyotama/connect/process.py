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

from libtmux import Pane, Server

from toyotama.connect.tube import Tube

logger = getLogger(__name__)


class Process(Tube):
    def __init__(
        self,
        path: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        timeout: float = 20.0,
    ):
        super().__init__()
        self.path: Path = Path(path)
        self.args: list[str] = args or []
        self.env: dict[str, str] = env or {}
        self.proc: subprocess.Popen | None
        self.returncode: int | None = None
        self.timeout: float = timeout

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
            logger.error(f'File not found: "{path}"')
            return
        except Exception as e:
            logger.error(f"Process.__init__(): {e}")
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
        returncode = self.proc.returncode
        if returncode is not None and self.returncode is None:
            self.returncode = returncode

            logger.error(f'"{self.path!s}" terminated: {signal.strsignal(-self.returncode)} (PID={self.proc.pid})')

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

        if self.proc.stdout is None:
            logger.warning("Process.recv(): stdout is None")
            return b""

        buf = b""
        try:
            buf += self.proc.stdout.read(n) or b""
        except Exception as e:
            logger.error(e)
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
            self.proc.stdin.write(payload)
            self.proc.stdin.flush()
        except OSError:
            logger.warning("Broken pipe")
        except Exception as e:
            logger.error(f"Process.send(): {e}")

    def gdb(self, script: list[str] | None = None, host: str = "localhost", port: int = 51280):
        self._gdbserver = subprocess.Popen(
            ["gdbserver", f"{host}:{port}", "--attach", str(self.pid)],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
        )

        master, slave = pty.openpty()
        tty.setraw(master)
        tty.setraw(slave)

        # tmux
        srv = Server()
        session = srv.sessions[0]

        window = session.new_window(attach=False, window_name="gdb")

        pane = Pane.from_pane_id(pane_id=window.pane_id, server=window.server)

        pane.send_keys(f"gdb -p {self.pid}")

        window.kill()

    def close(self):
        if self.proc is None:
            return

        if self.is_alive():
            self.proc.stdin.close()
            self.proc.stdout.close()
            self.proc.kill()
            self.proc.wait()
            logger.info(f'"{self.path!s}" killed (PID={self.proc.pid})')

        self.proc = None

    def __del__(self):
        self.close()
