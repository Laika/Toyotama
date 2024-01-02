import re
from pathlib import Path

import lief
import r2pipe

from ..pwn.address import Address
from ..util import MarkdownTable
from ..util.log import get_logger

logger = get_logger()


class ELF:
    def __init__(self, path: str, level: int = 4):
        self.elf = lief.parse(path)

        self.path = Path(path)

        self._base = 0x000000

        logger.info('[%s] Open "%s"', self.__class__.__name__, self.path)
        self._r = r2pipe.open(path)

        logger.info("[%s] %s", self.__class__.__name__, "a" * level)
        self._r.cmd("a" * level)

        self._funcs = self._get_funcs()
        self._relocs = self._get_relocs()
        self._strs = self._get_strs()
        self._info = self._get_info()
        self._syms = self._get_syms()

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, value: int) -> None:
        self._base = value

    def rop_gadget(self, pattern: str):
        gadgets = set()
        for gadget in self._get_rop_gadget(pattern):
            for opcode in gadget["opcodes"]:
                if opcode["opcode"].strip() == pattern.strip():
                    gadgets.add(self._base + opcode["offset"])
                    break

        return gadgets

    def r2(self, cmd: str) -> dict:
        results = self._r.cmdj(cmd)
        return results

    def got(self, target: str = "") -> dict[str, int] | int | None:
        if not target:
            return {reloc["name"]: self._base + reloc["vaddr"] for reloc in self._relocs if "name" in reloc.keys()}

        for reloc in self._relocs:
            if "name" in reloc.keys() and re.search(target, reloc["name"]):
                return Address(self._base + reloc["vaddr"])

        return None

    def plt(self, target: str = "") -> dict[str, int] | int | None:
        if not target:
            return {func["name"]: self._base + func["offset"] for func in self._funcs}

        for func in self._funcs:
            if re.search(target, func["name"]):
                return Address(self._base + func["offset"])

        return None

    def str(self, target: str = "") -> dict[str, int] | int | None:
        if not target:
            return {str_["string"]: self._base + str_["vaddr"] for str_ in self._strs}

        for str_ in self._strs:
            if re.search(target, str_["string"]):
                return Address(self._base + str_["vaddr"])

        return None

    def sym(self, target: str = "") -> dict[str, int] | int | None:
        if not target:
            return {sym["name"]: self._base + sym["vaddr"] for sym in self._syms}

        for sym in self._syms:
            if re.search(target, sym["name"]):
                return Address(self._base + sym["vaddr"])

        return None

    def _get_rop_gadget(self, pattern: str):
        results = self._r.cmdj(f"/Rj {pattern}")
        return results

    def _get_funcs(self) -> dict[str, int]:
        results = self._r.cmdj("aflj")
        return results

    def _get_relocs(self) -> dict[str, int]:
        results = self._r.cmdj("irj")
        return results

    def _get_strs(self) -> dict[str, int]:
        results = self._r.cmdj("izj")
        return results

    def _get_info(self) -> dict[str]:
        results = self._r.cmdj("iIj")
        return results

    def _get_syms(self) -> dict[str, int]:
        results = self._r.cmdj("isj")
        return results

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

    def asm(address: int, assembly):
        self.bin[address] = assembly

    def save(self, name: str):
        with open(name, "wb") as f:
            f.write(self.bin)
        log.info(f"Saved {name!s}")

    def find(self, target) -> dict:
        results = {}
        results |= {"plt": self.plt(target)}
        results |= {"str": self.str(target)}
        results |= {"sym": self.sym(target)}
        results |= {"got": self.got(target)}
        return results

    # alias
    relocs = got
    funcs = plt
    __repr__ = __str__
