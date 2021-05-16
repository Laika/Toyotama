import sys
from namedtuple import namedtuple

color = {
    "RESET": "\x1b[0m",
    "BOLD": "\x1b[1m",
    "FG_RED": f"\x1b[38;5;{0xdc};{0x35};{0x45}m",
    "BG_RED": f"\x1b[48;5;{0xdc};{0x35};{0x45}m",
    "GREEN": "\x1b[38;5;2m",
    "FG_YELLOW": f"\x1b[38;5;{0xff};{0xc1};{0x07}m",
    "BG_YELLOW": f"\x1b[48;5;{0xff};{0xc1};{0x07}m",
    "FG_BLUE": "\x1b[38;5;4m",
    "BG_BLUE": "\x1b[48;5;4m",
    "FG_MAGENTA": "\x1b[38;5;5m",
    "BG_MAGENTA": "\x1b[48;5;5m",
    "CYAN": "\x1b[38;5;6m",
    "PURPLE": "\x1b[38;5;93m",
    "VIOLET": "\x1b[38;5;128m",
    "FG_VIOLET": f"\x1b[38;5;{0x80};{0x00};{0x80}m",
    "BG_VIOLET": f"\x1b[48;5;{0x80};{0x00};{0x80}m",
    "FG_DEEPPURPLE": f"\x1b[38;5;{0x70};{0x00};{0x70}m",
    "BG_DEEPPURPLE": f"\x1b[48;5;{0x70};{0x00};{0x70}m",
    "FG_ORANGE": f"\x1b[38;5;{0xff};{0xc1};{0x07}m",
    "BG_ORANGE": f"\x1b[48;5;{0xff};{0xc1};{0x07}m",
    "DARK_GREY": "\x1b[38;5;240m",
    "GREY": "\x1b[38;5;246m",
    "FG_WHITE": f"\x1b[38;5;{0xff};{0xff};{0xff}m",
    "BG_WHITE": f"\x1b[48;5;{0xff};{0xff};{0xff}m",
    "FG_BLACK": f"\x1b[38;5;{0x00};{0x00};{0x00}m",
    "BG_BLACK": f"\x1b[48;5;{0x00};{0x00};{0x00}m",
}
Style = namedtuple("Style", color.keys())(**color)


class Logger:
    def __init__(self, fd=sys.stderr):
        self.fd = fd

    def __message(self, color: str, header: str, message: str):
        self.fd.write(f"{Style.BOLD}{color}{header} {message}{Style.RESET}\n")

    def colored(self, color: str, message: str):
        self.__message(color, "", message)

    def information(self, message: str):
        self.__message(f"{Style.BG_BLUE}{Style.FG_WHITE}", " INFO ", message)

    def progress(self, message: str):
        self.__message(f"{Style.BG_VIOLET}{Style.FG_WHITE}", " PROG ", message)

    def warning(self, message: str):
        self.__message(f"{Style.BG_ORANGE}{Style.FG_BLACK}", " WARN ", message)

    def error(self, message: str):
        self.__message(f"{Style.BG_RED}{Style.FG_WHITE}", " ERROR ", message)

    def send(self, message: str):
        self.__message(f"{Style.BG_DEEPPURPLE}{Style.FG_WHITE}", " <<SEND ", message)

    def recv(self, message: str):
        self.__message(f"{Style.BG_DEEPPURPLE}{Style.FG_WHITE}", " >>RECV ", message)
