from pathlib import Path

from toyotama.util.log import get_logger
from toyotama.elf.const import *
from toyotama.elf.elfstruct import *

logger = get_logger()


class MyELF(object):
    def __init__(self, path: str):
        self.path = Path(path)
        self.Ehdr = {}
        self.parser = ELFParser(Path(path))

    def is_elf(self) -> bool:
        return self.parser.is_elf()


class ELFParser(object):
    def __init__(self, path: Path):
        self.path = path

        with open(self.path, "rb") as f:
            self.map = f.read()

        if not self.is_elf():
            raise ValueError(f'"{self.path.name}" is not a vadid ELF file.')

    def is_elf(self) -> bool:
        return self.map[EI_MAG0] == ELFMAG0 and self.map[EI_MAG1] == ELFMAG1 and self.map[EI_MAG2] == ELFMAG2 and self.map[EI_MAG3] == ELFMAG3

    def parse_ehdr(self):
        # e_ident
        self.bits = 64 if self.map[EI_CLASS] == ELFCLASS64 else 32

        if self.bits == 64:
            ehdr = Elf64_Ehdr()

        e_ident = self.map[0:EI_NIDENT]


if __name__ == "__main__":
    elf = MyELF("../../example/vaccine")
    elf = MyELF(__file__)
