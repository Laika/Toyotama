import logging
import sys
from collections import namedtuple

WIDTH = 8

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


def rgb_to_ansi_color_code(rgb: str) -> str:
    rgb = rgb.lstrip("#")
    assert len(rgb) == 6
    r, g, b = map(lambda x: int(x, 16), (rgb[0:2], rgb[2:4], rgb[4:6]))
    return r, g, b


def fg(rgb) -> str:
    r, g, b = rgb_to_ansi_color_code(rgb)
    return f"\x1b[38;2;{r};{g};{b}m"


def bg(rgb) -> str:
    r, g, b = rgb_to_ansi_color_code(rgb)
    return f"\x1b[48;2;{r};{g};{b}m"


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


class CustomFormatter(logging.Formatter):
    def __init__(self, colored=True):
        self.fmt = "[%(levelname)s] %(message)s"
        self.date_format = "%Y-%m-%dT%T"
        self.FORMATS = {}
        if colored:
            self.FORMATS = {
                logging.DEBUG: Style.FG_GRAY + self.fmt + Style.RESET,
                logging.INFO: Style.FG_BLUE + self.fmt + Style.RESET,
                logging.WARNING: Style.FG_YELLOW + self.fmt + Style.RESET,
                logging.ERROR: Style.FG_RED + self.fmt + Style.RESET,
                logging.CRITICAL: Style.FG_DEEPPURPLE + self.fmt + Style.RESET,
            }
        else:
            self.FORMATS = {
                logging.DEBUG: self.fmt,
                logging.INFO: self.fmt,
                logging.WARNING: self.fmt,
                logging.ERROR: self.fmt,
                logging.CRITICAL: self.fmt,
            }

    def format(self, record):
        log_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_format, self.date_format)
        return formatter.format(record)


def get_logger(name="toyotama", loglevel="INFO", colored=True):
    logging._srcfile = None
    logging.logThreads = False
    logging.logProcesses = False
    logging.logMultiprocessing = False

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    loglevel = getattr(logging, loglevel.upper(), logging.INFO)
    logger.setLevel(loglevel)

    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter(colored=colored))
    logger.addHandler(handler)

    return logger
