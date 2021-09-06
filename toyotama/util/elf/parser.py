from pathlib import Path

from toyotama.util.integer import Int32, Int64, UInt16, UInt32, UInt64, UInt8
from toyotama.util.log import Logger
from toyotama.util.util import DotDict

from . import const
from . import struct


log = Logger()
# Basic types (32bit)


class Elf32_Addr(UInt32):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "UInt32"


class Elf32_Off(UInt32):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "UInt32"


class Elf32_Section(UInt16):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "UInt32"


class Elf32_Versym(UInt32):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "UInt32"


class Elf_Byte(UInt8):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "UInt8"


class Elf32_Half(UInt16):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "UInt16"


class Elf32_Sword(Int32):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "Int32"
        self.size = 4


class Elf32_Word(UInt32):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "UInt32"
        self.size = 4


class Elf32_Sxword(Int64):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "Int64"
        self.size = 8


class Elf32_Xword(UInt64):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "UInt64"
        self.size = 8


# Basic types (64bit)
class Elf64_Addr(UInt32):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "UInt32"
        self.size = 4


class Elf64_Off(UInt32):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "UInt32"
        self.size = 4


class Elf64_Section(UInt16):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "UInt32"
        self.size = 4


class Elf64_Versym(UInt32):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "UInt32"
        self.size = 4


class Elf64_Half(UInt16):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "UInt16"
        self.size = 2


class Elf64_Sword(Int32):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "Int32"
        self.size = 4


class Elf64_Word(UInt32):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "UInt32"
        self.size = 4


class Elf64_Sxword(Int64):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "Int64"
        self.size = 8


class Elf64_Xword(UInt64):
    def __init__(self, value):
        super().__init__(self, value)
        self.type = "UInt64"
        self.size = 8



class Elf_Ehdr(struct.Struct):
    def __init__(self):
        super().__init__()


class ELF:
    def __init__(self, filename: str, bits: int = 32):
        self._filename = Path(filename)
        self._fp = open(filename, "rb")
        self.symbol = DotDict()
        self.got = DotDict()
        self.plt = DotDict()
        self.function = DotDict()
        self.endian = 'little'
        self.address = 0x400000

        self.Elf_Ehdr = struct.Struct(
            "Elf32_Ehdr",
            {
                "e_ident": [UInt8 for _ in range(const.EI_NIDENT)],
                "e_type": UInt16,
                "e_machine": UInt16,
                "e_version": UInt32,
                "e_entry": Elf32_Addr,
                "e_phoff": Elf32_Off,
                "e_shoff": Elf32_Off,
                "e_flags": UInt32,
                "e_ehsize": UInt16,
                "e_phentsize": UInt16,
                "e_phnum": UInt16,
                "e_shentsize": UInt16,
                "e_shnum": UInt16,
                "e_shstrndx": UInt16,
            }
        ) if bits == 32 else struct.Struct(
            "Elf64_Ehdr",
            {
                "e_ident": [UInt8 for _ in range(const.EI_NIDENT)],
                "e_type": UInt16,
                "e_machine": UInt16,
                "e_version": UInt32,
                "e_entry": Elf64_Addr,
                "e_phoff": Elf64_Off,
                "e_shoff": Elf64_Off,
                "e_flags": UInt32,
                "e_ehsize": UInt16,
                "e_phentsize": UInt16,
                "e_phnum": UInt16,
                "e_shentsize": UInt16,
                "e_shnum": UInt16,
                "e_shstrndx": UInt16,
            }
        )

    def _check(self):
        self.elf_header.check()

    def get_symbol(self, name):
        ...

    def _parse(self, header):
        # Parse e_ident
        # EI_MAG
        EI_MAG = self._fp.read(4)
        check_EI_MAG = EI_MAG == bytes([const.EI_MAG0, const.EI_MAG1, const.EI_MAG2, const.EI_MAG3])
        print(check_EI_MAG)

    def __del__(self):
        if self._fp:
            self._fp.close()


def main():
    elf = ELF("/bin/true")
    elf._parse()


if __name__ == "__main__":
    main()
