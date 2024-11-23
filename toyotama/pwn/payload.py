import os
from collections.abc import Callable
from typing import Literal, Self

from colored import Fore, Style

from toyotama.pwn.address import Address
from toyotama.pwn.util import p32, p64


class Payload:
    def __init__(self, bits: Literal[32, 64] = 64):
        self.blocks: list[bytes] = []
        self.bits: Literal[32, 64] = bits
        self.bytes_: Literal[4, 8] = bits // 8
        self.packer: Callable[[int], bytes] = {
            32: p32,
            64: p64,
        }[bits]

    def __repr__(self) -> str:
        return f"Payload(blocks={self.blocks},bits={self.bits})"

    def visualize(self, columns: int = 8):
        entire = []
        payload = self.dump()
        n = len(payload)

        for i in range(0, (n + columns - 1) // columns):
            addr = f"{Fore.rgb(100,100,100)}{i*columns:#06x}{Style.reset}"

            hexdump, dump = [], []
            for j in range(columns):
                idx = i * columns + j
                if idx < n:
                    hexdump.append(f"{payload[idx]:02x}")
                    if 0x20 <= payload[idx] < 0x7F:
                        dump.append(chr(payload[idx]))
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
        self.blocks.append(byte * n)

    def zfill(self):
        self.fill(-len(self.dump()) % self.bytes_)

    def dump(self) -> bytes:
        return b"".join(self.blocks)

    def hexdump(self) -> str:
        return self.dump().hex()

    def __add__(self, other: Self | bytes | Address | int) -> Self:
        if isinstance(other, Payload):
            self.blocks += other.blocks
            return self

        elif isinstance(other, bytes):
            self.blocks.append(other)
            return self

        elif isinstance(other, Address):
            self.blocks.append(self.packer(other))
            return self

        elif isinstance(other, int):
            self.blocks.append(self.packer(other))
            return self

        else:
            raise TypeError(f"unsupported operand type(s) for +: 'Payload' and '{type(other)}'")

    def __iadd__(self, other) -> Self:
        return self.__add__(other)

    def add(self, other) -> Self:
        return self.__add__(other)

    def save(self, path: str):
        with open(path, "wb") as f:
            f.write(self.dump())
