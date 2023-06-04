from toyotama.util.integer import UChar, UInt16, UInt32, Int32, Int64
from dataclasses import dataclass
from toyotama.elf.const import *


@dataclass
class Elf32_Ehdr(object):
    e_ident: list[UChar]  # ELF "magic number"
    e_type: UInt16
    e_machine: UInt16
    e_version: UInt32
    e_entry: Elf32_Addr  # Entry point virtual address
    e_phoff: Elf32_Off  # Program header table file offset
    e_shoff: Elf32_Off  # Section header table file offset
    e_flags: UInt32
    e_ehsize: UInt16
    e_phentsize: UInt16
    e_phnum: UInt16
    e_shentsize: UInt16
    e_shnum: UInt16
    e_shstrndx: UInt16


@dataclass
class Elf64_Ehdr(object):
    e_ident: list[UChar]  # ELF "magic number"
    e_type: UInt16
    e_machine: UInt16
    e_version: UInt32
    e_entry: Elf64_Addr  # Entry point virtual address
    e_phoff: Elf64_Off  # Program header table file offset
    e_shoff: Elf64_Off  # Section header table file offset
    e_flags: UInt32
    e_ehsize: UInt16
    e_phentsize: UInt16
    e_phnum: UInt16
    e_shentsize: UInt16
    e_shnum: UInt16
    e_shstrndx: UInt16


# Program Header

## p_type
PT_NULL = 0
PT_LOAD = 1
PT_DYNAMIC = 2
PT_INTERP = 3
PT_NOTE = 4
PT_SHLIB = 5
PT_PHDR = 6
PT_TLS = 7  # Thread local storage segment
PT_LOOS = 0x60000000  # OS-specific
PT_HIOS = 0x6FFFFFFF  # OS-specific
PT_LOPROC = 0x70000000
PT_HIPROC = 0x7FFFFFFF
PT_GNU_EH_FRAME = PT_LOOS + 0x474E550
PT_GNU_STACK = PT_LOOS + 0x474E551
PT_GNU_RELRO = PT_LOOS + 0x474E552
PT_GNU_PROPERTY = PT_LOOS + 0x474E553

## p_flgas
PF_X = 0x1
PF_W = 0x2
PF_R = 0x4

## sh_type
SHT_NULL = 0
SHT_PROGBITS = 1
SHT_SYMTAB = 2
SHT_STRTAB = 3
SHT_RELA = 4
SHT_HASH = 5
SHT_DYNAMIC = 6
SHT_NOTE = 7
SHT_NOBITS = 8
SHT_REL = 9
SHT_SHLIB = 10
SHT_DYNSYM = 11
SHT_NUM = 12
SHT_LOPROC = 0x70000000
SHT_HIPROC = 0x7FFFFFFF
SHT_LOUSER = 0x80000000
SHT_HIUSER = 0xFFFFFFFF

## sh_flags
SHF_WRITE = 0x1
SHF_ALLOC = 0x2
SHF_EXECINSTR = 0x4
SHF_RELA_LIVEPATCH = 0x00100000
SHF_RO_AFTER_INIT = 0x00200000
SHF_MASKPROC = 0xF0000000


@dataclass
class Elf32_Phdr(object):
    p_type: UInt32
    p_offset: Elf32_Off
    p_vaddr: Elf32_Addr
    p_paddr: Elf32_Addr
    p_filesz: UInt32
    p_memsz: UInt32
    p_flags: UInt32
    p_align: UInt32


@dataclass
class Elf64_Phdr(object):
    p_type: UInt32
    p_flags: UInt32
    p_offset: Elf64_Off
    p_vaddr: Elf64_Addr
    p_paddr: Elf64_Addr
    p_filesz: UInt64
    p_memsz: UInt64
    p_align: UInt64


# Section header (Shdr)
@dataclass
class Elf32_Shdr(object):
    sh_name: UInt32
    sh_type: UInt32
    sh_flags: UInt32
    sh_addr: Elf32_Addr
    sh_offset: Elf32_Off
    sh_size: UInt32
    sh_link: UInt32
    sh_info: UInt32
    sh_addralign: UInt32
    sh_entsize: UInt32


@dataclass
class Elf64_Shdr(object):
    sh_name: UInt32
    sh_type: UInt32
    sh_flags: UInt64
    sh_addr: Elf64_Addr
    sh_offset: Elf64_Off
    sh_size: UInt64
    sh_link: UInt32
    sh_info: UInt32
    sh_addralign: UInt64
    sh_entsize: UInt64


# String and symbol tables
@dataclass
class Elf32_Sym(object):
    st_name: UInt32
    st_value: Elf32_Addr
    st_size: UInt32
    st_info: UChar
    st_other: UChar
    st_shndx: UInt16


@dataclass
class Elf64_Sym(object):
    st_name: UInt32
    st_info: UChar
    st_other: UChar
    st_shndx: UInt16
    st_value: Elf64_Addr
    st_size: UInt64


# Relocation entries (Rel & Rela)
@dataclass
class Elf32_Rel(object):
    r_offset: Elf32_Addr
    r_info: UInt32


@dataclass
class Elf64_Rel(object):
    r_offset: Elf64_Addr
    r_info: UInt64


@dataclass
class Elf32_Rela(object):
    r_offset: Elf32_Addr
    r_info: UInt32
    r_addend: Int32


@dataclass
class Elf64_Rela(object):
    r_offset: Elf64_Addr
    r_info: UInt64
    r_addend: Int64


# Dynamic tags (Dyn)
class Elf32_Dyn(object):
    d_tag: Elf32_Word
    d_val: Elf32_Word  # Union d_un
    d_ptr: Elf32_Addr  # Union d_un


class Elf64_Dyn(object):
    d_tag: Elf32_Word
    d_val: Elf64_Xword  # Union d_un
    d_ptr: Elf64_Addr  # Union d_un


_DYNAMIC32: list[Elf32_Dyn]
_DYNAMIC64: list[Elf64_Dyn]


# Notes (Nhdr)
@dataclass
class Elf32_Nhdr(object):
    n_namesz: Elf32_Word
    n_descsz: Elf32_Word
    n_type: Elf32_Word


@dataclass
class Elf64_Nhdr(object):
    n_namesz: Elf64_Word
    n_descsz: Elf64_Word
    n_type: Elf64_Word
