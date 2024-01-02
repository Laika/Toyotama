from log import get_logger

logger = get_logger(__name__)


class BitStream:
    def __init__(self, value: bytes | int | str, string_limit: int = 200):
        self.bitstream: list[int] = []
        self.string_limit = string_limit
        self.flip_mask = 0

        if isinstance(value, bytes):
            self.bitstream = sum([list(int(c) ^ self.flip_mask for c in f"{byte:08b}") for byte in value], [])

        if isinstance(value, int):
            self.bitstream = [int(c) ^ self.flip_mask for c in f"{value:b}"]

        if isinstance(value, str):
            if any(c not in ("0", "1") for c in value):
                print(f"The value contains non-binary characters {value}")
                return
            self.bitstream = [int(c) ^ self.flip_mask for c in value]
            print(self.bitstream)

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
        self.index = 0
        return self

    def __next__(self):
        if self.index == len(self.bitstream):
            raise StopIteration
        result = self.bitstream[self.index]
        self.index += 1
        return result

    def __int__(self) -> int:
        x = 0
        for b in self.bitstream:
            x <<= 1
            x |= b ^ self.flip_mask
        return x

    def __bytes__(self) -> bytes:
        x = int(self)
        return x.to_bytes((x.bit_length() + 7) // 8, "big")

    def __len__(self) -> int:
        return len(self.bitstream)

    def __lshift__(self, n: int) -> "BitStream":
        self.bitstream = self.bitstream[n:]
        return self

    def __rshift__(self, n: int) -> "BitStream":
        self.bitstream = self.bitstream[:-n]
        return self

    def flip(self):
        self.flip_mask = 1 - self.flip_mask

    def __invert__(self) -> "BitStream":
        self.flip()
        return self


if __name__ == "__main__":
    bs = BitStream(
        "1100010100001111101011000001111011011110010010000110111110101011000111011001011000111110011001101000001001110001100101101111010"
    )
    bs = BitStream(b"b\x87\xd6\x0fo$7\xd5\x8e\xcb\x1f3A8\xcbz")
    bs = BitStream(130969645321298197535138324414870375290)
    print(bs)

    print(int(bs))
    print(bytes(bs))

    print(bs)
    print(~bs)
