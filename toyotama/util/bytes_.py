import base64
from logging import getLogger
from typing import Self

logger = getLogger(__name__)


class Bytes(bytes):
    def __xor__(self, other):
        if not isinstance(other, bytes):
            return NotImplemented
        if len(self) != len(other):
            logger.warning("XOR: length of bytes is not equal")
        return Bytes(x ^ y for x, y in zip(self, other))

    def __rxor__(self, other):
        if isinstance(other, bytes):
            return Bytes(self.__xor__(other))
        return NotImplemented

    def __or__(self, other):
        if isinstance(other, bytes):
            return Bytes(super().__add__(other))
        return NotImplemented

    def __ror__(self, other):
        if isinstance(other, bytes):
            return Bytes(other.__add__(self))
        return NotImplemented

    def __getitem__(self, key: int | slice) -> int | Self:
        result = super().__getitem__(key)
        if isinstance(key, slice):
            return Bytes(result)
        return result  # int for int index

    def to_int(self):
        return int.from_bytes(self, "big")

    @staticmethod
    def from_int(n: int):
        length = (n.bit_length() + 7) // 8 or 1  # at least 1 byte
        return Bytes(n.to_bytes(length, "big"))

    def to_block(self, block_size: int = 16) -> list[Self]:
        return [self[i : i + block_size] for i in range(0, len(self), block_size)]

    def to_base64(self) -> str:
        return base64.b64encode(self).decode()

    @staticmethod
    def from_base64(s: str | bytes) -> Self:
        if isinstance(s, (str, bytes)):
            return Bytes(base64.b64decode(s))
        raise TypeError("Expected str or bytes")
