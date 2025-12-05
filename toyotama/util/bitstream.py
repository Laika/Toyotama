from logging import getLogger

logger = getLogger(__name__)


class BitStream:
    def __init__(self, value: bytes | int | str, string_limit: int = 200):
        self.bitstream: list[int] = []
        self.string_limit = string_limit
        self.flip_mask = 0

        if isinstance(value, bytes):
            self.bitstream = [int(c) for byte in value for c in f"{byte:08b}"]
        elif isinstance(value, int):
            self.bitstream = [int(c) for c in f"{value:b}"] if value else [0]
        elif isinstance(value, str):
            if any(c not in ("0", "1") for c in value):
                raise ValueError(f"The value contains non-binary characters: '{value}'")
            self.bitstream = [int(c) for c in value]
        else:
            raise TypeError(f"Expected bytes, int, or str, got {type(value).__name__}")

    def __str__(self) -> str:
        s = "".join(str(b ^ self.flip_mask) for b in self.bitstream[: self.string_limit])
        if len(self.bitstream) > self.string_limit:
            s += "..."
        return s

    def __repr__(self) -> str:
        s = str(self)
        s = f"BitStream({s})"
        return s

    def __iter__(self):
        return iter(self.bitstream)

    def __int__(self) -> int:
        x = 0
        for b in self.bitstream:
            x <<= 1
            x |= b ^ self.flip_mask
        return x

    def __bytes__(self) -> bytes:
        x = int(self)
        length = (x.bit_length() + 7) // 8 or 1
        return x.to_bytes(length, "big")

    def __len__(self) -> int:
        return len(self.bitstream)

    def _copy_with_bits(self, bits: list[int]) -> "BitStream":
        """Create a new BitStream with the given bits, preserving settings."""
        new = BitStream("0")
        new.bitstream = bits
        new.flip_mask = self.flip_mask
        new.string_limit = self.string_limit
        return new

    def __lshift__(self, n: int) -> "BitStream":
        return self._copy_with_bits(self.bitstream[n:])

    def __rshift__(self, n: int) -> "BitStream":
        if n == 0:
            return self._copy_with_bits(self.bitstream[:])
        return self._copy_with_bits(self.bitstream[:-n])

    def flip(self):
        """Flip the bits in-place."""
        self.flip_mask = 1 - self.flip_mask

    def __invert__(self) -> "BitStream":
        new = self._copy_with_bits(self.bitstream[:])
        new.flip_mask = 1 - self.flip_mask
        return new


if __name__ == "__main__":
    bs = BitStream("1100010100001111101011000001111011011110010010000110111110101011000111011001011000111110011001101000001001110001100101101111010")
    bs = BitStream(b"b\x87\xd6\x0fo$7\xd5\x8e\xcb\x1f3A8\xcbz")
    bs = BitStream(130969645321298197535138324414870375290)
    print(bs)

    print(int(bs))
    print(bytes(bs))

    print(bs)
    print(~bs)
