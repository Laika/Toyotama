import base64
from logging import getLogger
from typing import Self

logger = getLogger(__name__)


class Bytes(bytes):
    def __xor__(self, other: Self) -> Self:
        if len(self) != len(other):
            logger.warning("XOR: length of bytes is not equal")
        return Bytes(x ^ y for x, y in zip(self, other))

    def __rxor__(self, other: bytes) -> Self:
        if isinstance(other, bytes):
            return Bytes(self.__xor__(other))
        raise NotImplemented

    def __or__(self, other: Self) -> Self:
        if isinstance(other, Bytes):
            return Bytes(super().__add__(other))
        elif isinstance(other, bytes):
            return Bytes(super().__add__(other))
        raise NotImplemented

    def __ror__(self, other: Self) -> Self:
        if isinstance(other, Bytes):
            return Bytes(other.__add__(self))
        elif isinstance(other, bytes):
            return Bytes(other.__add__(self))
        raise NotImplemented

    def __getitem__(self, key: int | slice) -> Self:
        return Bytes(super().__getitem__(key))

    def to_int(self):
        return int.from_bytes(self, "big")

    @staticmethod
    def from_int(n: int):
        return Bytes(n.to_bytes((n.bit_length() + 7) // 8, "big"))

    def to_block(self, block_size: int = 16) -> list[Self]:
        return [self[i : i + block_size] for i in range(0, len(self), block_size)]

    def to_base64(self) -> str:
        return base64.b64encode(self).decode()

    @staticmethod
    def from_base64(s: str | bytes | Self) -> Self:
        if isinstance(s, bytes):
            return Bytes(base64.b64decode(s))
        elif isinstance(s, Bytes):
            return Bytes(base64.b64decode(s))
        elif isinstance(s, str):
            return Bytes(base64.b64decode(s.encode()))
        else:
            raise TypeError("Expected str, bytes or Bytes")
