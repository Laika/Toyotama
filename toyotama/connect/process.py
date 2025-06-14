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
        args: list[str],
        env: dict[str, str] | None = None,
        timeout: float | None = None,
        raw_mode: bool = True,
        cwd: Path | None = None,
        stdin: int | None = None,
        stdout: int | None = None,
        stderr: int | None = None,
    ):
        super().__init__()
        self._args: list[str] = args or []
        self._env: dict[str, str] = env or {}
        self._proc: subprocess.Popen | None
        self._returncode: int | None = None
        self._timeout: float | None = timeout

        master, slave = None, None
        if raw_mode:
            master, slave = pty.openpty()
            tty.setraw(master)
            tty.setraw(slave)
            stdout = slave

        stdin = stdin or subprocess.PIPE
        stdout = stdout or subprocess.PIPE
        stderr = stderr or subprocess.STDOUT

        try:
            self._proc = subprocess.Popen(
                self._args,
                env=self._env,
                cwd=cwd,
                shell=False,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
            )
        except FileNotFoundError:
            logger.error('File not found: "%s"', self._args[0])
            return
        except Exception as e:
            logger.error("Process.__init__(): %s", e)
            return

        self._path = Path(self._args[0])

        if not hasattr(self._proc, "stdout"):
            logger.error("Process.__init__(): Failed to open a pipe")
            return

        if master is not None:
            self._proc.stdout = os.fdopen(os.dup(master), "r+b", 0)
            os.close(master)

        fd = self._proc.stdout.fileno()  # pyright: ignore
        fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)

        logger.info("Created a new process (PID: %d)", self._proc.pid)

    @property
    def proc(self) -> subprocess.Popen | None:
        return self._proc

    @property
    def pid(self) -> int:
        return getattr(self._proc, "pid", -1)

    @property
    def path(self) -> Path:
        return self._path

    def poll(self) -> int | None:
        if self._proc is None:
            return None
        if self._proc.poll() is None:  # alive
            return None

        # dead
        if self._returncode is None:
            self._returncode = self._proc.returncode
            if self._proc.returncode != 0:
                if self._proc.returncode < 0:
                    logger.error('"%s" terminated: %s (PID=%d)', str(self._path), signal.strsignal(-self._proc.returncode), self.pid)
                else:
                    logger.error('"%s" terminated with exit code %d (PID=%d)', str(self._path), self._proc.returncode, self.pid)
            else:
                logger.info('"%s" terminated (PID=%d)', str(self._path), self.pid)

        return self._returncode

    def is_alive(self):
        return self.poll() is None

    def is_dead(self):
        return not self.is_alive()

    def is_ready(self) -> bool:
        if self._proc is None:
            return False

        if self._timeout is None:
            while self.is_alive():
                ready, [], [] = select.select([self._proc.stdout], [], [], 0.1)
                if ready:
                    return True
        else:
            ready = select.select([self._proc.stdout], [], [], self._timeout)
            if ready == ([], [], []):
                raise TimeoutError(f"Process.is_ready(): timeout {self._timeout}s")

        return True

    def recv(self, n: int = 0x1000) -> bytes:
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
            logger.error("Error reading from process stdout: %s", e)
            raise

        self.recv_bytes += len(buf)

        self.poll()

        return buf

    def send(self, message: bytes | str | int, term: bytes | str = b""):
        self.poll()

        payload = b""

        message = self._to_bytes(message)
        payload += message

        term = self._to_bytes(term)
        payload += term

        self.send_bytes += len(payload)

        try:
            self._proc.stdin.write(payload)  # pyright: ignore
            self._proc.stdin.flush()  # pyright: ignore
        except OSError:
            logger.warning("Broken pipe")
        except Exception as e:
            logger.exception("Process.send(): %s", e)

    def gdb(self, script: str = "", remote_work_dir: Path = Path("."), host: str = "127.0.0.1", port: int = 51280):
        gdbserver_args = ["sudo", "gdbserver", "--multi", f"{host}:{port}", "--attach", str(self.pid)]
        self._gdbserver = subprocess.Popen(
            gdbserver_args,
            shell=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            encoding="utf-8",
        )
        logger.info("gdbserver started (PID: %d): %s", self._gdbserver.pid, " ".join(gdbserver_args))

        # tmux
        srv = Server()
        session = srv.sessions[0]

        try:
            pane = session.active_window.active_pane
            if not pane:
                logger.error("Cannot get the active pane")
                return
            pane = pane.split(direction=PaneDirection.Right, shell="gdb")

            pane.send_keys(f"file {self._path!s}")
            pane.send_keys(f"set remote exec-file {self._path!s}")
            # pane.send_keys(f"remote put {self._path!s} {remote_work_dir/self.path.name}")
            pane.send_keys(f"target extended-remote {host}:{port}")
            for line in script.split(os.linesep):
                pane.send_keys(line)
            pane.send_keys("start")

        except Exception as e:
            logger.exception("Process.gdb(): %s", e)

    def close(self):
        if self._proc is None:
            return

        if self.is_alive():
            logger.info('"%s" killed (PID=%d)', self._path, self._proc.pid)
            self._proc.stdin.close()  # pyright: ignore
            self._proc.stdout.close()  # pyright: ignore
            self._proc.kill()
            self._proc.wait()
            self._proc = None

    def __del__(self):
        ...
        # self.close()
