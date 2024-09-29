import os
from collections.abc import Callable
from typing import Literal, Self

from colored import Fore, Style

from toyotama.pwn.address import Address
from toyotama.pwn.util import p32, p64


class Payload:
    def __init__(self, payload: bytes = b"", bits: Literal[32, 64] = 64):
        self.payload: bytes = payload
        self.bits: Literal[32, 64] = bits
        self.block_size: Literal[4, 8] = bits // 8
        self.packer: Callable[[int], bytes] = {
            32: p32,
            64: p64,
        }[bits]

    def __repr__(self) -> str:
        return f"Payload(payload={self.payload},bits={self.bits})"

    def visualize(self, columns: int = 8):
        entire = []
        n = len(self.payload)

        for i in range(0, (n + columns - 1) // columns):
            addr = f"{Fore.rgb(100,100,100)}{i*columns:#06x}{Style.reset}"

            hexdump, dump = [], []
            for j in range(columns):
                idx = i * columns + j
                if idx < n:
                    hexdump.append(f"{self.payload[idx]:02x}")
                    if 0x20 <= self.payload[idx] < 0x7F:
                        dump.append(chr(self.payload[idx]))
                    else:
                        dump.append(".")
                else:
                    hexdump.append("  ")
                    dump.append(" ")

            hexdump = " ".join(hexdump).center(columns * 3 - 1, " ")
            dump = "".join(dump).ljust(columns * 2, " ")

            entire.append(" │ ".join([addr, hexdump, dump]))

        print(os.linesep.join(entire))

    def fill(self, n: int, byte: bytes = b"A"):
        self.payload += byte * n

    def zfill(self):
        self.fill(-len(self.payload) % self.block_size)

    def dump(self) -> bytes:
        return self.payload

    def hexdump(self) -> str:
        return self.payload.hex()

    def __add__(self, other) -> Self:
        if isinstance(other, Payload):
            return Payload(self.payload + other.payload, bits=self.bits)

        elif isinstance(other, bytes):
            return Payload(self.payload + other, bits=self.bits)

        elif isinstance(other, Address):
            return Payload(self.payload + self.packer(other), bits=self.bits)

        elif isinstance(other, int):
            return Payload(self.payload + self.packer(other), bits=self.bits)

        else:
            raise TypeError(f"unsupported operand type(s) for +: 'Payload' and '{type(other)}'")

    def add(self, other) -> Self:
        return self.__add__(other)

    def save(self, path: str):
        with open(path, "wb") as f:
            f.write(self.payload)
