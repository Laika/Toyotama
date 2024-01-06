import ast
import io
import os
import re
from base64 import b64decode
from collections.abc import Callable
from typing import Any

from toyotama.util.log import get_logger

logger = get_logger(__name__, os.environ.get("TOYOTAMA_LOG_LEVEL", "INFO"))


class Text(io.StringIO):
    """A class to parse text."""

    PATTERN_RAW = r" *(?P<name>.*?) *[=:] *(?P<value>.*)"
    pattern = re.compile(PATTERN_RAW)

    def readvalue(self, parser: Callable = ast.literal_eval) -> Any:
        """Read a value from the next line.
        Args:
            parser (Callable): A function to parse the value.

        Examples:
        >>> text = Text("a = 1\nb = [2, 5]")
        >>> text.readvalue()
        1
        >>> text.readvalue()
        [2, 5]

        Returns:
            Any: The value parsed by the parser.
        """
        line = self.pattern.match(self.readline())
        if not line:
            return None
        name = line.group("name").strip()
        value = parser(line.group("value"))

        logger.debug(f"{name}: {value}")

        return value

    def readint(self) -> int:
        """Read an integer from the next line.

        Args:
            parser (Callable): A function to parse the value.

        Examples:
        >>> text = Text("a = 1\nb: 0x2abc")
        >>> text.readint()
        1
        >>> text.readint()
        10940

        Returns:
            int: The value parsed by the parser.
        """
        return self.readvalue(parser=lambda x: int(x, 0))

    def readhex(self) -> bytes:
        """Read a hex value from the next line.

        Args:
            parser (Callable): A function to parse the value.

        Examples:
        >>> text = Text("b = '2abc'")
        >>> text.readhex()
        b'*\xbc'

        Returns:
            bytes: The value parsed by the parser.
        """

        return self.readvalue(parser=lambda x: bytes.fromhex(x))

    def readbase64(self) -> bytes:
        """Read a base64 value from the next line.

        Args:
            parser (Callable): A function to parse the value.

        Examples:
        >>> text = Text("b = 'aG9nZQ=='")
        hoge

        Returns:
            bytes: The value parsed by the parser.
        """

        return self.readvalue(parser=lambda x: b64decode(x))

    def update_pattern(self, pattern: str) -> None:
        """Update the pattern to parse the next line.

        Args:
            pattern (str): The pattern to parse the next line.
        """

        self.PATTERN_RAW = pattern
        self.pattern = re.compile(self.PATTERN_RAW)


__all__ = ["Text"]
