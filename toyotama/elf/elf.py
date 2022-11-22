from pathlib import Path

import r2pipe

from ..util import MarkdownTable
from ..util.log import get_logger

logger = get_logger()


class ELF:
    def __init__(self, filename: str, level: int = 4):
        self.filename = Path(filename)

        self._base = 0x000000
        logger.info(f"Open {self.filename!s}")
        self._r = r2pipe.open(filename)
        logger.info(f"[r2pipe] {'a'*level}")
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
            if "name" in reloc.keys() and reloc["name"] == target:
                return self._base + reloc["vaddr"]

        return None

    def plt(self, target: str = "") -> dict[str, int] | int | None:
        if not target:
            return {func["name"]: self._base + func["offset"] for func in self._funcs}

        for func in self._funcs:
            if func["name"].removeprefix("sym.").removeprefix("imp.") == target:
                return self._base + func["offset"]

        return None

    def str(self, target: str = "") -> dict[str, int] | int | None:
        if not target:
            return {str_["string"]: self._base + str_["vaddr"] for str_ in self._strs}

        for str_ in self._strs:
            if str_["string"] == target:
                return self._base + str_["vaddr"]

        return None

    def sym(self, target: str = "") -> dict[str, int] | int | None:
        if not target:
            return {sym["name"]: self._base + sym["vaddr"] for sym in self._syms}

        for sym in self._syms:
            if sym["name"] == target:
                return self._base + sym["vaddr"]

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
        result = f"{self.filename.resolve()!s}\n"
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

    # alias
    relocs = got
    funcs = plt
    __repr__ = __str__


class LIBC(ELF):
    def __init__(self, filename: str, level: int = 1):
        super().__init__(filename, level)
