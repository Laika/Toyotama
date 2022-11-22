from collections import namedtuple

RED = "#DC3545"
YELLOW = "#FFC107"
BLUE = "#1E8CFB"
GREEN = "#228B22"
MAGENTA = "#FF00FF"
CYAN = "#00FFFF"
VIOLET = "#800080"
DEEP_PURPLE = "#700070"
ORANGE = "#E05a00"
LIGHT_GRAY = "#C0C0C0"
GRAY = "#696969"
DARK_GRAY = "#282d33"
WHITE = "#FFFFFF"
BLACK = "#202020"


def hex_to_ansi_color_code(rgb: str) -> tuple[int, int, int]:
    rgb = rgb.lstrip("#")
    if len(rgb) != 6:
        return 0, 0, 0

    r, g, b = map(lambda x: int(x, 16), (rgb[0:2], rgb[2:4], rgb[4:6]))
    return r, g, b


def fg(rgb) -> str:
    r, g, b = hex_to_ansi_color_code(rgb)
    return f"\x1b[38;2;{r};{g};{b}m"


def bg(rgb) -> str:
    r, g, b = hex_to_ansi_color_code(rgb)
    return f"\x1b[48;2;{r};{g};{b}m"


styles = {
    "RESET": "\x1b[0m",
    "BOLD": "\x1b[1m",
    "ITALIC": "\x1b[3m",
    "UNDERLINE": "\x1b[4m",
    "BLINKING": "\x1b[5m",
    "FG_RED": fg(RED),
    "BG_RED": bg(RED),
    "FG_GREEN": fg(GREEN),
    "BG_GREEN": bg(GREEN),
    "FG_YELLOW": fg(YELLOW),
    "BG_YELLOW": bg(YELLOW),
    "FG_BLUE": fg(BLUE),
    "BG_BLUE": bg(BLUE),
    "FG_MAGENTA": fg(MAGENTA),
    "BG_MAGENTA": bg(MAGENTA),
    "FG_CYAN": fg(CYAN),
    "BG_CYAN": bg(CYAN),
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

Style = namedtuple("Style", list(styles.keys()))(**styles)
