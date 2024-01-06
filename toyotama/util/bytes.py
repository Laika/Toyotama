import base64
from typing import Self


class Bytes(bytes):
    def __xor__(self, other: Self) -> Self:
        if len(self) != len(other):
            raise ValueError("Bytes objects must be of same length")
        return Bytes(x ^ y for x, y in zip(self, other))

    def to_int(self):
        return int.from_bytes(self, "big")

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

    @staticmethod
    def from_int(n: int):
        return Bytes(n.to_bytes((n.bit_length() + 7) // 8, "big"))
