from toyotama.pwn.util import p8, p16, p32, p64


class Address(int):
    def __init__(self, address: int):
        super().__init__()
        self.address = address

    def __str__(self) -> str:
        res = hex(self.address)
        return res

    def hex(self) -> str:
        return hex(self.address)

    def __add__(self, o):
        if not isinstance(o, int):
            raise TypeError("Invalid type")

        return Address(self.address + o)

    def __sub__(self, o):
        if isinstance(o, Address):
            return Address(abs(self.address - o.address))

        elif isinstance(o, int):
            return Address(self.address - o)

        else:
            raise TypeError("Invalid type")

    def __iadd__(self, o):
        if not isinstance(o, int):
            raise TypeError("Invalid type")

        self.address += o

        return self

    def __isub__(self, o):
        if not isinstance(o, int):
            raise TypeError("Invalid type")

        self.address = abs(self.address - o)

        return self

    def p8(self) -> bytes:
        return p8(self.address)

    def p16(self) -> bytes:
        return p16(self.address)

    def p32(self) -> bytes:
        return p32(self.address)

    def p64(self) -> bytes:
        return p64(self.address)


Addr = Address
