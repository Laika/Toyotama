import sys
from collections import namedtuple

Style = namedtuple(
    "Style",
    "RESET BOLD RED GREEN YELLOW BLUE MAGENTA CYAN PURPLE VIOLET DEEP_PURPLE ORANGE DARK_GREY GREY",
)(
    RESET="\x1b[0m",
    BOLD="\x1b[1m",
    RED="\x1b[38;5;1m",
    GREEN="\x1b[38;5;2m",
    YELLOW="\x1b[38;5;3m",
    BLUE="\x1b[38;5;4m",
    MAGENTA="\x1b[38;5;5m",
    CYAN="\x1b[38;5;6m",
    PURPLE="\x1b[38;5;93m",
    VIOLET="\x1b[38;5;128m",
    DEEP_PURPLE="\x1b[38;5;161m",
    ORANGE="\x1b[38;5;166m",
    DARK_GREY="\x1b[38;5;240m",
    GREY="\x1b[38;5;246m",
)


class Logger:
    def __init__(self, fd=sys.stderr):
        self.fd = fd

    def __message(self, color: str, header: str, message: str):
        self.fd.write(f"{Style.BOLD}{color}{header} {message}{Style.RESET}\n")

    def colored(self, color: str, message: str):
        self.__message(color, "", message)

    def information(self, message: str):
        self.__message(Style.BLUE, "[+]", message)

    def progress(self, message: str):
        self.__message(Style.VIOLET, "[*]", message)

    def warning(self, message: str):
        self.__message(Style.ORANGE, "[!]", message)

    def error(self, message: str):
        self.__message(Style.RED, "[x]", message)
