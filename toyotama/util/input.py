import ast
import io
import re
from base64 import b64decode
from collections.abc import Callable
from typing import Any

from toyotama.util.log import get_logger

pattern_raw = r"(?P<name>.*?) *[=:] *(?P<value>.*)"
pattern = re.compile(pattern_raw)

logger = get_logger(__name__, "DEBUG")


def readvalue(f, parser: Callable = ast.literal_eval) -> Any:
    line = pattern.match(f.readline())
    if not line:
        return None
    name = line.group("name").strip()
    value = parser(line.group("value"))

    logger.debug(f"{name}: {value}")

    return value


def readint(f) -> int:
    return readvalue(f, parser=lambda x: int(x, 0))


def readhex(f) -> bytes:
    return readvalue(f, parser=lambda x: bytes.fromhex(x))


def readbase64(f) -> bytes:
    return readvalue(f, parser=lambda x: b64decode(x))


if __name__ == "__main__":
    test1 = io.StringIO("test1 = 3218973129837")
    assert readint(test1) == 3218973129837

    test2 = io.StringIO("test2: 3d330fa3cbed11")
    assert readhex(test2) == b"=3\x0f\xa3\xcb\xed\x11"

    test3 = io.StringIO("test3 : VEVTVFNUUklOR1Nob2dlaG9nZWhvZ2VmdWdh")
    assert readbase64(test3) == b"TESTSTRINGShogehogehogefuga"
