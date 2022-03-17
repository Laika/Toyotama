import os
import sys
from collections import namedtuple

WIDTH = 8


def rgb_to_ansi_color_code(rgb: str) -> str:
    rgb = rgb.lstrip("#")
    assert len(rgb) == 6
    r, g, b = rgb[0:2], rgb[2:4], rgb[4:6]
    return r, g, b


def fg(r, g, b) -> str:
    return f"\x1b[38;2;{r};{g};{b}m"


def bg(r, g, b) -> str:
    return f"\x1b[48;2;{r};{g};{b}m"


RED = "#DC3545"
YELLOW = "#FFC107"
BLUE = "#0057d9"
VIOLET = "#800080"
DEEP_PURPLE = "#700070"
ORANGE = "#E05a00"
LIGHT_GRAY = "#C0C0C0"
GRAY = "#696969"
DARK_GRAY = "#282d33"
WHITE = "#FFFFFF"
BLACK = "#202020"

color = {
    "RESET": "\x1b[0m",
    "BOLD": "\x1b[1m",
    "FG_RED": fg(RED),
    "BG_RED": bg(RED),
    "GREEN": "\x1b[38;5;2m",
    "FG_YELLOW": fg(YELLOW),
    "BG_YELLOW": bg(YELLOW),
    "FG_BLUE": fg(BLUE),
    "BG_BLUE": bg(BLUE),
    "FG_MAGENTA": "\x1b[38;5;5m",
    "BG_MAGENTA": "\x1b[48;5;5m",
    "CYAN": "\x1b[38;5;6m",
    "PURPLE": "\x1b[38;5;93m",
    "VIOLET": "\x1b[38;5;128m",
    "FG_VIOLET": fg(VIOLET),
    "BG_VIOLET": bg(VIOLET),
    "FG_DEEPPURPLE": fg(DEEP_PURPLE),
    "BG_DEEPPURPLE": bg(DEEP_PURPLE),
    "FG_ORANGE": fg(ORANGE),
    "BG_ORANGE": bg(ORANGE),
    "FG_LIGHTGRAY": fg(LIGHT_GRAY),
    "BG_LIGHTGRAY": bg(LIGHT_GRAY),
    "FG_GRAY": fg(GRAY),
    "BG_GRAY": bg(GRAY),
    "FG_DARKGRAY": fg(DARK_GRAY),
    "BG_DARKGRAY": bg(DARK_GRAY),
    "FG_WHITE": fg(WHITE),
    "BG_WHITE": bg(WHITE),
    "FG_BLACK": fg(BLACK),
    "BG_BLACK": bg(BLACK),
}

Style = namedtuple("Style", list(color.keys()))(**color)


class StdoutHook:
    def __init__(self):
        self.newline_count = 0

    def write(self, text: str):
        sys.__stdout__.write(text)
        self.newline_count += text.count(os.linesep)

    def flush(self):
        sys.__stdout__.flush()


class StderrHook:
    def __init__(self):
        self.newline_count = 0

    def write(self, text: str):
        sys.__stderr__.write(text)
        self.newline_count += text.count(os.linesep)

    def flush(self):
        sys.__stderr__.flush()


class Logger:
    def __init__(self):
        self.fd = sys.stderr
        self.ongoing_func = set()

    def __message(self, color: str, header: str, message: str):
        self.fd.write(f"{color}{header}{Style.RESET}  {message}\n")

    def colored(self, color: str, message: str):
        self.__message(color, "", message)

    def information(self, message: str):
        self.__message(Style.BG_BLUE + Style.FG_WHITE, "INFO".center(WIDTH, " "), message)

    def progress(self, message: str):
        self.__message(Style.BG_VIOLET + Style.FG_WHITE, "PROG".center(WIDTH, " "), message)

    def warning(self, message: str):
        self.__message(Style.BG_YELLOW + Style.FG_BLACK, "WARN".center(WIDTH, " "), message)

    def error(self, message: str):
        self.__message(Style.BG_RED + Style.FG_WHITE, "FAIL".center(WIDTH, " "), message)

    def send(self, message: str):
        self.__message(Style.BG_GRAY + Style.FG_BLACK, "SEND".center(WIDTH, " "), message)

    def recv(self, message: str):
        self.__message(Style.BG_DARKGRAY + Style.FG_WHITE, "RECV".center(WIDTH, " "), message)

    def watch(self, func):
        def wrapper(*args, **kwargs):
            self.ongoing_func.add(func)
            self.__message(
                Style.BG_DEEPPURPLE + Style.FG_WHITE,
                "RUN".center(WIDTH, " "),
                f"{func.__name__}({','.join(map(str, args))})",
            )
            return_value = func(*args, **kwargs)
            self.fd.write(f"\x1b[{sys.stdout.newline_count+1}F")
            self.fd.write("\x1b[2K")
            self.__message(
                Style.BG_DARKGRAY + Style.FG_WHITE,
                "DONE".center(WIDTH, " "),
                f"{func.__name__}({','.join(map(str, args))})",
            )
            self.fd.write(f"\x1b[{sys.stdout.newline_count}E")
            self.ongoing_func.discard(func)
            return return_value

        return wrapper
