import sys
from enum import IntEnum

class Color(IntEnum):
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    PURPLE = 93
    VIOLET = 128
    DEEP_PURPLE = 161
    ORANGE = 166
    DARK_GREY = 240
    GREY = 246

reset = '\x1b[0m'
bold  = '\x1b[1m'
fg    = lambda c: f'\x1b[38;5;{c}m'
bg    = lambda c: f'\x1b[48;5;{c}m'
colorify = lambda c, m: f'{fg(c)}{m}{reset}'

message = lambda c, h, m : sys.stderr.write(f"{bold}{fg(c)}{h} {m}{reset}\n")
info  = lambda m: message(Color.BLUE, '[+]', m)
proc  = lambda m: message(Color.VIOLET, '[*]', m)
warn  = lambda m: message(Color.ORANGE, '[!]', m)
error = lambda m: message(Color.RED, '[-]', m)

