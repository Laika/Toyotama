from typing import Self


class Bytes(bytes):
    def __xor__(self, other: Self) -> Self:
        if len(self) != len(other):
            raise ValueError("Bytes objects must be of same length")
        return Bytes(x ^ y for x, y in zip(self, other))

    def to_int(self):
        return int.from_bytes(self, "big")

    @staticmethod
    def from_int(n: int):
        return Bytes(n.to_bytes((n.bit_length() + 7) // 8, "big"))
