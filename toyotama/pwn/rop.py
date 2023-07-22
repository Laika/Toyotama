from toyotama.pwn.address import Address
from toyotama.pwn.util import p64


class ROP:
    def __init__(self):
        self.chain = []

    def __add__(self, o):
        self.chain.append(o)

    def __iadd__(self, o):
        return self.__add__(o)

    def dump(self, pack=p64) -> bytes:
        payload = b""
        for x in self.chain:
            if isinstance(x, int):
                payload += pack(x)
            elif isinstance(x, Address):
                payload += pack(x.address)
            else:
                raise TypeError(f"Unsupported type: {type(x)}")

        return payload
