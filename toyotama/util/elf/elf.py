from pathlib import Path

import r2pipe

from ..util import MarkdownTable


class ELF:
    def __init__(self, filename: str, analyze_level: int = 4):
        self.filename = Path(filename)
        self.base = 0x000000
        self.__r = r2pipe.open(filename)
        self.__r.cmd("a" * analyze_level)
        self.plt = self.__get_functions()
        self.got = self.__get_relocations()
        self.string = self.__get_strings()
        self.info = self.__get_information()
        self.symbols = self.__get_symbols()

    def __get_functions(self):
        functions = self.__r.cmdj("aflj")
        results = {function.name: self.base + function.offset for function in functions.values()}
        return results

    def __get_relocations(self):
        relocations = self.__r.cmdj("irj")
        results = {relocation.name: self.base + relocation.vaddr for relocation in relocations.values() if "name" in relocation.keys()}
        return results

    def __get_strings(self):
        strings = self.__r.cmdj("izj")
        results = {string.string: self.base + string.vaddr for string in strings.values()}
        return results

    def __get_information(self):
        info = self.__r.cmdj("iIj")
        return info

    def __get_symbols(self):
        symbols = self.__r.cmdj("isj")
        results = {symbol.name: self.base + symbol.vaddr for symbol in symbols.values()}
        return results

    def __str__(self):
        enabled = lambda x: "Enabled" if x else "Disabled"
        result = f"{self.filename.resolve()!s}\n"
        mt = MarkdownTable(
            rows=[
                ["Arch", self.info.arch],
                ["RELRO", self.info.relro.title()],
                ["Canary", enabled(self.info.canary)],
                ["NX", enabled(self.info.nx)],
                ["PIE", enabled(self.info.pic)],
            ]
        )
        result += mt.dump()

        return result

    __repr__ = __str__
