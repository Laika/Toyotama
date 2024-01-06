from logging import StreamHandler, getLogger
from os import getenv

from .ad import *
from .connect import *
from .elf import *
from .pwn import *
from .terminal import *
from .util import *
from .web import *

logger = getLogger("toyotama")
logger.setLevel(getenv("TOYOTAMA_LOG_LEVEL", "INFO").upper())
handler = StreamHandler()
formatter = CustomFormatter(colored=bool(getenv("TOYOTAMA_LOG_COLORED", True)))
handler.setFormatter(formatter)
logger.addHandler(handler)

from .crypto import *
