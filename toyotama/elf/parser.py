from pathlib import Path

from toyotama.elf.const import *
from toyotama.elf.elfstruct import Elf64_Ehdr
from toyotama.util.log import get_logger

logger = get_logger()


class ParseError(Exception):
    pass


class ELFParser:
    def __init__(self, path: Path):
        self.path = path

        self.fd = open(self.path, "rb")

        self.parse_ehdr()


    def __repr__(self) -> str:
        return f'ELFParser(path="{self.path.resolve()}")'

    __str__ = __repr__

    def parse_ehdr(self):
        logger.info("Parsing ELF header...")
        self.ehdr = Elf64_Ehdr()
        self.fd.readinto(self.ehdr)

        if not self.is_elf():
            raise ParseError(f'"{self.path.name}" is not a valid ELF file.')

        self.bits = ELFClass.from_int(self.ehdr.e_ident[EI_CLASS]).bits()
        self.endian = ELFData.from_int(self.ehdr.e_ident[EI_DATA]).endian()

        logger.info("bits = %d", self.bits)
        logger.info("endianness = %s", self.endian)

        self.e_entry = self.ehdr.e_entry
        self.e_phoff = self.ehdr.e_phoff
        self.e_shoff = self.ehdr.e_shoff
        self.e_flags = self.ehdr.e_flags
        self.e_ehsize = self.ehdr.e_ehsize
        self.e_phentsize = self.ehdr.e_phentsize
        self.e_phnum = self.ehdr.e_phnum
        self.e_shentsize = self.ehdr.e_shentsize
        self.e_shnum = self.ehdr.e_shnum
        self.e_shstrndx = self.ehdr.e_shstrndx

        logger.info("e_entry = %#x", self.e_entry)
        logger.info("e_phoff = %#x", self.e_phoff)
        logger.info("e_shoff = %#x", self.e_shoff)
        logger.info("e_flags = %#x", self.e_flags)
        logger.info("e_ehsize = %#x", self.e_ehsize)
        logger.info("e_phentsize = %#x", self.e_phentsize)
        logger.info("e_phnum = %#x", self.e_phnum)
        logger.info("e_shentsize = %#x", self.e_shentsize)
        logger.info("e_shnum = %#x", self.e_shnum)
        logger.info("e_shstrndx = %#x", self.e_shstrndx)

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
