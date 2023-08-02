from pathlib import Path

from toyotama.elf.const import *
from toyotama.elf.elfstruct import Elf64_Ehdr
from toyotama.util.log import get_logger

logger = get_logger()


class ELFParser:
    def __init__(self, path: Path):
        self.path = path

        self.fd = open(self.path, "rb")

        self.parse_ehdr()

    def parse_ehdr(self):
        self.ehdr = Elf64_Ehdr()
        self.fd.readinto(self.ehdr)

        if not self.is_elf():
            raise ValueError(f'"{self.path.name}" is not a valid ELF file.')

        self.bits = ELFClass.from_int(self.ehdr.e_ident[EI_CLASS]).bits()
        self.endian = ELFData.from_int(self.ehdr.e_ident[EI_DATA]).endian()

        print("bits", self.bits)
        print("endianness", self.endian)

        return self.ehdr

    def is_elf(self) -> bool:
        return (
            self.ehdr.e_ident[EI_MAG0] == ELFMAG0
            and self.ehdr.e_ident[EI_MAG1] == ELFMAG1
            and self.ehdr.e_ident[EI_MAG2] == ELFMAG2
            and self.ehdr.e_ident[EI_MAG3] == ELFMAG3
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fd:
            self.fd.close()


if __name__ == "__main__":
    parser = ELFParser(Path("./chall"))
    print(parser)
