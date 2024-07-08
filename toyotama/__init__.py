import logging
from os import getenv

from rich.logging import RichHandler

from .connect import *
from .elf import *
from .pwn import *
from .terminal import *
from .util import *
from .web import *

logger = logging.getLogger("toyotama")
logger.setLevel(getenv("TOYOTAMA_LOG_LEVEL", "INFO").upper())
handler = RichHandler(rich_tracebacks=True)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)

from .crypto import *
