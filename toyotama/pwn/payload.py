from collections.abc import Callable
from typing import Literal, Self

from .address import Address
from .util import p32, p64


class Payload:
    def __init__(self, payload: bytes = b"", bits: Literal[32, 64] = 64):
        self.payload: bytes = payload
        self.bits: Literal[32, 64] = bits
        self.block_size: Literal[4, 8] = bits // 8
        self.packer: Callable[[int], bytes] = {
            32: p32,
            64: p64,
        }[bits]

    def fill(self, n: int, byte: bytes = b"A"):
        self.payload += byte * n

    def zfill(self):
        self.fill(-len(self.payload) % self.block_size)

    def dump(self) -> bytes:
        return self.payload

    def hexdump(self) -> str:
        return self.payload.hex()

    def __lshift__(self, other) -> Self:
        if isinstance(other, Payload):
            return Payload(self.payload + other.payload, bits=self.bits)

        elif isinstance(other, bytes):
            return Payload(self.payload + other, bits=self.bits)

        elif isinstance(other, Address):
            return Payload(self.payload + other.pack(), bits=self.bits)

        elif isinstance(other, int):
            return Payload(self.payload + self.packer(other), bits=self.bits)

        else:
            raise TypeError(f"unsupported operand type(s) for +: 'Payload' and '{type(other)}'")

    def add(self, other) -> Self:
        return self.__lshift__(other)

    def save(self, path: str):
        with open(path, "wb") as f:
            f.write(self.payload)
