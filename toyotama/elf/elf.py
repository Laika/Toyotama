import re
from logging import getLogger
from pathlib import Path
from typing import Any

import lief
import rzpipe

from toyotama.pwn.address import Address
from toyotama.util.util import MarkdownTable

logger = getLogger(__name__)


class ELF:
    def __init__(self, path: str, level: int = 4):
        self.elf = lief.parse(path)

        self.path = Path(path)

        self._base = Address(0x0)

        self._rz = rzpipe.open(path)

        logger.info("[%s] %s", self.__class__.__name__, "a" * level)
        self._rz.cmd("a" * level)

        self._funcs = self._get_funcs()
        self._relocs = self._get_relocs()
        self._strs = self._get_strs()
        self._info = self._get_info()
        self._syms = self._get_syms()

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, value: Address) -> None:
        self._base = value

    def addr(self, offset: int) -> Address:
        return Address(self._base + offset)

    def rop_gadget(self, pattern: str):
        gadgets = set()
        for gadget in self._get_rop_gadget(pattern):
            for opcode in gadget["opcodes"]:
                if opcode["opcode"].strip() == pattern.strip():
                    gadgets.add(self._base + opcode["offset"])
                    break

        return gadgets

    def r2(self, cmd: str) -> dict:
        results = self._rz.cmdj(cmd)
        return results or {}

    def got(self, target: str) -> Address | None:
        for reloc in self._relocs:
            if "name" in reloc.keys() and re.search(target, reloc["name"]):
                logger.debug("[got] %s: 0x%x", reloc["name"], reloc["vaddr"])
                return Address(self._base + reloc["vaddr"])

        return None

    def gots(self) -> dict[str, Address]:
        return {reloc["name"]: Address(self._base + reloc["vaddr"]) for reloc in self._relocs if "vaddr" in reloc.keys()}

    def plt(self, target: str) -> Address | None:
        for func in self._funcs:
            if re.search(target, func["name"]):
                return Address(self._base + func["offset"])

        return None

    def plts(self) -> dict[str, Address]:
        return {func["name"]: Address(self._base + func["offset"]) for func in self._funcs if "offset" in func.keys()}

    def str(self, target: str) -> Address | None:
        for str_ in self._strs:
            if re.search(target, str_["string"]):
                return Address(self._base + str_["vaddr"])

        logger.warning("Not found %s", target)
        return None

    def strs(self) -> dict[str, Address]:
        return {str_["string"]: Address(self._base + str_["vaddr"]) for str_ in self._strs if "vaddr" in str_.keys()}

    def sym(self, target: str) -> Address | None:
        for sym in self._syms:
            if re.search(target, sym["name"]):
                logger.debug("[sym] %s: 0x%x", sym["name"], sym["vaddr"])
                return Address(self._base + sym["vaddr"])

        logger.warning("Not found %s", target)
        return None

    def syms(self) -> dict[str, Address]:
        return {sym["name"]: Address(self._base + sym["vaddr"]) for sym in self._syms if "vaddr" in sym.keys()}

    def _get_rop_gadget(self, pattern: str) -> dict[str, int]:
        results = self._rz.cmdj(f"/Rj {pattern}")
        return results or {}

    def _get_funcs(self) -> dict[str, int]:
        results = self._rz.cmdj("aflj")
        return results or {}

    def _get_relocs(self) -> dict[str, int]:
        results = self._rz.cmdj("irj")
        return results or {}

    def _get_strs(self) -> dict[str, int]:
        results = self._rz.cmdj("izj")
        return results or {}

    def _get_info(self) -> dict[str, Any]:
        results = self._rz.cmdj("iIj")
        return results or {}

    def _get_syms(self) -> dict[str, int]:
        results = self._rz.cmdj("isj")
        return results or {}

    def __str__(self):
        enabled = lambda x: "Enabled" if x else "Disabled"
        result = f"{self.path.resolve()!s}\n"
        mt = MarkdownTable(
            rows=[
                ["Arch", self._info["arch"]],
                ["RELRO", self._info["relro"].title()],
                ["Canary", enabled(self._info["canary"])],
                ["NX", enabled(self._info["nx"])],
                ["PIE", enabled(self._info["pic"])],
                ["Lang", self._info["lang"]],
            ]
        )
        result += mt.dump()

        return result

    def find(self, target) -> dict:
        results = {}
        results |= {"plt": self.plt(target)}
        results |= {"str": self.str(target)}
        results |= {"sym": self.sym(target)}
        results |= {"got": self.got(target)}
        return results

    def close(self):
        ...

    # alias
    __repr__ = __str__


class LIBC(ELF):
    def __init__(self, path: str, level: int = 2):
        super().__init__(path, level)
