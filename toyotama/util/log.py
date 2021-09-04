import os
import sys
from collections import namedtuple

WIDTH = 8

color = {
    "RESET": "\x1b[0m",
    "BOLD": "\x1b[1m",
    "FG_RED": f"\x1b[38;2;{0xdc};{0x35};{0x45}m",
    "BG_RED": f"\x1b[48;2;{0xdc};{0x35};{0x45}m",
    "GREEN": "\x1b[38;5;2m",
    "FG_YELLOW": f"\x1b[38;2;{0xff};{0xc1};{0x07}m",
    "BG_YELLOW": f"\x1b[48;2;{0xff};{0xc1};{0x07}m",
    "FG_BLUE": f"\x1b[38;2;{0x00};{0x57};{0xd9}m",
    "BG_BLUE": f"\x1b[48;2;{0x00};{0x57};{0xd9}m",
    "FG_MAGENTA": "\x1b[38;5;5m",
    "BG_MAGENTA": "\x1b[48;5;5m",
    "CYAN": "\x1b[38;5;6m",
    "PURPLE": "\x1b[38;5;93m",
    "VIOLET": "\x1b[38;5;128m",
    "FG_VIOLET": f"\x1b[38;2;{0x80};{0x00};{0x80}m",
    "BG_VIOLET": f"\x1b[48;2;{0x80};{0x00};{0x80}m",
    "FG_DEEPPURPLE": f"\x1b[38;2;{0x70};{0x00};{0x70}m",
    "BG_DEEPPURPLE": f"\x1b[48;2;{0x70};{0x00};{0x70}m",
    "FG_ORANGE": f"\x1b[38;2;{0xe0};{0x5a};{0x00}m",
    "BG_ORANGE": f"\x1b[48;2;{0xe0};{0x5a};{0x00}m",
    "FG_LIGHTGRAY": f"\x1b[38;2;{0xc0};{0xc0};{0xc0}m",
    "BG_LIGHTGRAY": f"\x1b[48;2;{0xc0};{0xc0};{0xc0}m",
    "FG_GRAY": f"\x1b[38;2;{0x69};{0x69};{0x69}m",
    "BG_GRAY": f"\x1b[48;2;{0x69};{0x69};{0x69}m",
    "FG_DARKGRAY": f"\x1b[38;2;{0x28};{0x2d};{0x33}m",
    "BG_DARKGRAY": f"\x1b[48;2;{0x28};{0x2d};{0x33}m",
    "FG_WHITE": f"\x1b[38;2;{0xff};{0xff};{0xff}m",
    "BG_WHITE": f"\x1b[48;2;{0xff};{0xff};{0xff}m",
    "FG_BLACK": f"\x1b[38;2;{0x20};{0x20};{0x20}m",
    "BG_BLACK": f"\x1b[48;2;{0x20};{0x20};{0x20}m",
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
