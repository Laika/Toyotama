from ctypes import c_char, c_int32, c_int64, c_uint16, c_uint32, c_uint64, Structure

from .const import EI_NIDENT, Elf32_Addr, Elf32_Off, Elf32_Word, Elf64_Addr, Elf64_Off, Elf64_Word, Elf64_Xword


class Elf32_Ehdr(Structure):
    _fields_ = (
        ("e_ident", c_char * EI_NIDENT),
        ("e_type", c_uint16),
        ("e_machine", c_uint16),
        ("e_version", c_uint32),
        ("e_entry", Elf32_Addr),
        ("e_phoff", Elf32_Off),
        ("e_shoff", Elf32_Off),
        ("e_flags", c_uint32),
        ("e_ehsize", c_uint16),
        ("e_phentsize", c_uint16),
        ("e_phnum", c_uint16),
        ("e_shentsize", c_uint16),
        ("e_shnum", c_uint16),
        ("e_shstrndx", c_uint16),
    )


class Elf64_Ehdr(Structure):
    _fields_ = (
        ("e_ident", c_char * EI_NIDENT),
        ("e_type", c_uint16),
        ("e_machine", c_uint16),
        ("e_version", c_uint32),
        ("e_entry", Elf64_Addr),
        ("e_phoff", Elf64_Off),
        ("e_shoff", Elf64_Off),
        ("e_flags", c_uint32),
        ("e_ehsize", c_uint16),
        ("e_phentsize", c_uint16),
        ("e_phnum", c_uint16),
        ("e_shentsize", c_uint16),
        ("e_shnum", c_uint16),
        ("e_shstrndx", c_uint16),
    )


# Program Header
# p_type
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

# p_flgas
PF_X = 0x1
PF_W = 0x2
PF_R = 0x4

# sh_type
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

# sh_flags
SHF_WRITE = 0x1
SHF_ALLOC = 0x2
SHF_EXECINSTR = 0x4
SHF_RELA_LIVEPATCH = 0x00100000
SHF_RO_AFTER_INIT = 0x00200000
SHF_MASKPROC = 0xF0000000


class Elf32_Phdr(Structure):
    _fields_ = (
        ("p_type", c_uint32),
        ("p_offset", Elf32_Off),
        ("p_vaddr", Elf32_Addr),
        ("p_paddr", Elf32_Addr),
        ("p_filesz", c_uint32),
        ("p_memsz", c_uint32),
        ("p_flags", c_uint32),
        ("p_align", c_uint32),
    )


class Elf64_Phdr(Structure):
    _fields_ = (
        ("p_type", c_uint32),
        ("p_flags", c_uint32),
        ("p_offset", Elf64_Off),
        ("p_vaddr", Elf64_Addr),
        ("p_paddr", Elf64_Addr),
        ("p_filesz", c_uint64),
        ("p_memsz", c_uint64),
        ("p_align", c_uint64),
    )


# Section header (Shdr)
class Elf32_Shdr(Structure):
    _fields_ = (
        ("sh_name", c_uint32),
        ("sh_type", c_uint32),
        ("sh_flags", c_uint32),
        ("sh_addr", Elf32_Addr),
        ("sh_offset", Elf32_Off),
        ("sh_size", c_uint32),
        ("sh_link", c_uint32),
        ("sh_info", c_uint32),
        ("sh_addralign", c_uint32),
        ("sh_entsize", c_uint32),
    )


class Elf64_Shdr(Structure):
    _fields_ = (
        ("sh_name", c_uint32),
        ("sh_type", c_uint32),
        ("sh_flags", c_uint64),
        ("sh_addr", Elf64_Addr),
        ("sh_offset", Elf64_Off),
        ("sh_size", c_uint64),
        ("sh_link", c_uint32),
        ("sh_info", c_uint32),
        ("sh_addralign", c_uint64),
        ("sh_entsize", c_uint64),
    )


# String and symbol tables
class Elf32_Sym(Structure):
    _fields_ = (
        ("st_name", c_uint32),
        ("st_value", Elf32_Addr),
        ("st_size", c_uint32),
        ("st_info", c_char),
        ("st_other", c_char),
        ("st_shndx", c_uint16),
    )


class Elf64_Sym(Structure):
    _fields_ = (
        ("st_name", c_uint32),
        ("st_info", c_char),
        ("st_other", c_char),
        ("st_shndx", c_uint16),
        ("st_value", Elf64_Addr),
        ("st_size", c_uint64),
    )


# Relocation entries (Rel & Rela)
class Elf32_Rel(Structure):
    _fields_ = (
        ("r_offset", Elf32_Addr),
        ("r_info", c_uint32),
    )


class Elf64_Rel(Structure):
    _fields_ = (
        ("r_offset", Elf64_Addr),
        ("r_info", c_uint64),
    )


class Elf32_Rela(Structure):
    _fields_ = (
        ("r_offset", Elf32_Addr),
        ("r_info", c_uint32),
        ("r_addend", c_int32),
    )


class Elf64_Rela(Structure):
    _fields_ = (
        ("r_offset", Elf64_Addr),
        ("r_info", c_uint64),
        ("r_addend", c_int64),
    )


# Dynamic tags (Dyn)
class Elf32_Dyn(Structure):
    _fields_ = (
        ("d_tag", Elf32_Word),
        ("d_val", Elf32_Word),  # Union d_un
        ("d_ptr", Elf32_Addr),  # Union d_un
    )


class Elf64_Dyn(Structure):
    _fields_ = (
        ("d_tag", Elf32_Word),
        ("d_val", Elf64_Xword),  # Union d_un
        ("d_ptr", Elf64_Addr),  # Union d_un
    )


_DYNAMIC32: list[Elf32_Dyn]
_DYNAMIC64: list[Elf64_Dyn]


# Notes (Nhdr)
class Elf32_Nhdr(Structure):
    _fields_ = (
        ("n_namesz", Elf32_Word),
        ("n_descsz", Elf32_Word),
        ("n_type", Elf32_Word),
    )


class Elf64_Nhdr(Structure):
    _fields_ = (
        ("n_namesz", Elf64_Word),
        ("n_descsz", Elf64_Word),
        ("n_type", Elf64_Word),
    )


if __name__ == "__main__":
    ehdr = Elf64_Ehdr()
    print(ehdr)
