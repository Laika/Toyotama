from ctypes import c_char, c_int32, c_int64, c_uint16, c_uint32, c_uint64
from enum import IntEnum

# Basic types
Elf32_Addr = c_uint32
Elf32_Off = c_uint32
Elf32_Section = c_uint16
Elf32_Versym = c_uint16
Elf_Byte = c_char
Elf32_Half = c_uint16
Elf32_Sword = c_int32
Elf32_Word = c_uint32
Elf32_Sxword = c_int64
Elf32_Xword = c_uint64


Elf64_Addr = c_uint64
Elf64_Off = c_uint64
Elf64_Section = c_uint16
Elf64_Versym = c_uint16
Elf64_Half = c_uint16
Elf64_Sword = c_int32
Elf64_Word = c_uint32
Elf64_Sxword = c_int64
Elf64_Xword = c_uint64


# ELF header (Ehdr)
EI_NIDENT = 16

# e_ident
EI_MAG0 = 0
EI_MAG1 = 1
EI_MAG2 = 2
EI_MAG3 = 3
EI_CLASS = 4
EI_DATA = 5
EI_VERSION = 6
EI_OSABI = 7
EI_PAD = 8

ELFMAG0 = 0x7F
ELFMAG1 = 0x45
ELFMAG2 = 0x4C
ELFMAG3 = 0x46
ELFMAG = b"\177ELF"
SELFMAG = 4


class ELFClass(IntEnum):
    NONE = 0
    BIT32 = 1
    BIT64 = 2
    NUM = 3

    @classmethod
    def from_int(cls, x: int) -> "ELFClass":
        match x:
            case 1:
                return cls.BIT32
            case 2:
                return cls.BIT64
            case 3:
                return cls.NUM
            case _:
                return cls.NONE

    def bits(self) -> int:
        match self.value:
            case self.BIT32:
                return 32
            case self.BIT64:
                return 64
            case _:
                raise ValueError("Invalid ELF class")


class ELFData(IntEnum):
    NONE = 0
    LSB = 1
    MSB = 2
    NUM = 3

    @classmethod
    def from_int(cls, x: int):
        match x:
            case 1:
                return cls.LSB
            case 2:
                return cls.MSB
            case 3:
                return cls.NUM
            case _:
                return cls.NONE

    def endian(self):
        match self.value:
            case self.LSB:
                return "little"
            case self.MSB:
                return "big"
            case _:
                raise ValueError("Invalid ELF data")


# e_type
ET_NONE = 0
ET_REL = 1
ET_EXEC = 2
ET_DYN = 3
ET_CORE = 4

# e_machine
EM_NONE = 0
EM_M32 = 1
EM_SPARC = 2
EM_386 = 3
EM_68K = 4
EM_88K = 5
EM_486 = 6  # Perhaps disused
EM_860 = 7
EM_MIPS = 8  # MIPS R3000 (officially, big-endian only)

"""Next two are historical and binaries and modules of these types will be rejected by Linux."""
EM_MIPS_RS3_LE = 10  # MIPS R3000 little-endian
EM_MIPS_RS4_BE = 10  # MIPS R4000 big-endian

EM_PARISC = 15  # HPPA
EM_SPARC32PLUS = 18  # Sun's "v8plus"
EM_PPC = 20  # PowerPC
EM_PPC64 = 21  # PowerPC64
EM_SPU = 23  # Cell BE SPU
EM_ARM = 40  # ARM 32 bit
EM_SH = 42  # SuperH
EM_SPARCV9 = 43  # SPARC v9 64-bit
EM_H8_300 = 46  # Renesas H8/300
EM_IA_64 = 50  # HP/Intel IA-64
EM_X86_64 = 62  # AMD x86-64
EM_S390 = 22  # IBM S/390
EM_CRIS = 76  # Axis Communications 32-bit embedded processor
EM_M32R = 88  # Renesas M32R
EM_MN10300 = 89  # Panasonic/MEI MN10300, AM33
EM_OPENRISC = 92  # OpenRISC 32-bit embedded processor
EM_ARCOMPACT = 93  # ARCompact processor
EM_XTENSA = 94  # Tensilica Xtensa Architecture
EM_BLACKFIN = 106  # ADI Blackfin Processor
EM_UNICORE = 110  # UniCore-32
EM_ALTERA_NIOS2 = 113  # Altera Nios II soft-core processor
EM_TI_C6000 = 140  # TI C6X DSPs
EM_HEXAGON = 164  # QUALCOMM Hexagon
EM_NDS32 = 167  # Andes Technology compact code size embedded RISC processor family

EM_AARCH64 = 183  # ARM 64 bit
EM_TILEPRO = 188  # Tilera TILEPro
EM_MICROBLAZE = 189  # Xilinx MicroBlaze
EM_TILEGX = 191  # Tilera TILE-Gx
EM_ARCV2 = 195  # ARCv2 Cores
EM_RISCV = 243  # RISC-V
EM_BPF = 247  # Linux BPF - in-kernel virtual machine
EM_CSKY = 252  # C-SKY
EM_LOONGARCH = 258  # LoongArch
EM_FRV = 0x5441  # Fujitsu FR-V


EM_ALPHA = 0x9026  # This is an interim value that we will use until the committee comes up with a final number.


EM_CYGNUS_M32R = 0x9041  # Bogus old m32r magic number, used by old tools.


EM_S390_OLD = 0xA390  # This is the old interim value for S/390 architecture


EM_CYGNUS_MN10300 = 0xBEEF  # Also Panasonic/MEI MN10300, AM33


# e_version
EV_NONE = 0
EV_CURRENT = 1

# e_phnum
PN_XNUM = 0xFFFF

# special section indexes
SHN_UNDEF = 0
SHN_LORESERVE = 0xFF00
SHN_LOPROC = 0xFF00
SHN_HIPROC = 0xFF1F
SHN_LIVEPATCH = 0xFF20
SHN_ABS = 0xFFF1
SHN_COMMON = 0xFFF2
SHN_HIRESERVE = 0xFFFF


# This info is needed when parsing the symbol table
STB_LOCAL = 0
STB_GLOBAL = 1
STB_WEAK = 2

STT_NOTYPE = 0
STT_OBJECT = 1
STT_FUNC = 2
STT_SECTION = 3
STT_FILE = 4
STT_COMMON = 5
STT_TLS = 6


def ELF_ST_BIND(x: int) -> int:
    return x >> 4


def ELF_ST_TYPE(x: int) -> int:
    return x & 0xF


def ELF32_ST_BIND(x: int) -> int:
    return ELF_ST_BIND(x)


def ELF32_ST_TYPE(x: int) -> int:
    return ELF_ST_TYPE(x)


def ELF64_ST_BIND(x: int) -> int:
    return ELF_ST_BIND(x)


def ELF64_ST_TYPE(x: int) -> int:
    return ELF_ST_TYPE(x)


def ELF32_R_SYM(x: int) -> int:
    return x >> 8


def ELF32_R_TYPE(x: int) -> int:
    return x & 0xFF


def ELF64_R_SYM(x: int) -> int:
    return x >> 32


def ELF64_R_TYPE(x: int) -> int:
    return x & 0xFFFFFFFF


# This is the info that is needed to parse the dynamic section of the file
DT_NULL = 0
DT_NEEDED = 1
DT_PLTRELSZ = 2
DT_PLTGOT = 3
DT_HASH = 4
DT_STRTAB = 5
DT_SYMTAB = 6
DT_RELA = 7
DT_RELASZ = 8
DT_RELAENT = 9
DT_STRSZ = 10
DT_SYMENT = 11
DT_INIT = 12
DT_FINI = 13
DT_SONAME = 14
DT_RPATH = 15
DT_SYMBOLIC = 16
DT_REL = 17
DT_RELSZ = 18
DT_RELENT = 19
DT_PLTREL = 20
DT_DEBUG = 21
DT_TEXTREL = 22
DT_JMPREL = 23
DT_ENCODING = 32
OLD_DT_LOOS = 0x60000000
DT_LOOS = 0x6000000D
DT_HIOS = 0x6FFFF000
DT_VALRNGLO = 0x6FFFFD00
DT_VALRNGHI = 0x6FFFFDFF
DT_ADDRRNGLO = 0x6FFFFE00
DT_ADDRRNGHI = 0x6FFFFEFF
DT_VERSYM = 0x6FFFFFF0
DT_RELACOUNT = 0x6FFFFFF9
DT_RELCOUNT = 0x6FFFFFFA
DT_FLAGS_1 = 0x6FFFFFFB
DT_VERDEF = 0x6FFFFFFC
DT_VERDEFNUM = 0x6FFFFFFD
DT_VERNEED = 0x6FFFFFFE
DT_VERNEEDNUM = 0x6FFFFFFF
OLD_DT_HIOS = 0x6FFFFFFF
DT_LOPROC = 0x70000000
DT_HIPROC = 0x7FFFFFFF


"""
Notes used in ET_CORE. Architectures export some of the arch register sets
using the corresponding note types via the PTRACE_GETREGSET and
PTRACE_SETREGSET requests.
The note name for all these is "LINUX".
"""
NT_PRSTATUS = 1
NT_PRFPREG = 2
NT_PRPSINFO = 3
NT_TASKSTRUCT = 4
NT_AUXV = 6
"""
Note to userspace developers: size of NT_SIGINFO note may increase
in the future to accomodate more fields, don't assume it is fixed!
"""
NT_SIGINFO = 0x53494749
NT_FILE = 0x46494C45
NT_PRXFPREG = 0x46E62B7F  # copied from gdb5.1/include/elf/common.h */
NT_PPC_VMX = 0x100  # PowerPC Altivec/VMX registers
NT_PPC_SPE = 0x101  # PowerPC SPE/EVR registers
NT_PPC_VSX = 0x102  # PowerPC VSX registers
NT_PPC_TAR = 0x103  # Target Address Register
NT_PPC_PPR = 0x104  # Program Priority Register
NT_PPC_DSCR = 0x105  # Data Stream Control Register
NT_PPC_EBB = 0x106  # Event Based Branch Registers
NT_PPC_PMU = 0x107  # Performance Monitor Registers
NT_PPC_TM_CGPR = 0x108  # TM checkpointed GPR Registers
NT_PPC_TM_CFPR = 0x109  # TM checkpointed FPR Registers
NT_PPC_TM_CVMX = 0x10A  # TM checkpointed VMX Registers
NT_PPC_TM_CVSX = 0x10B  # TM checkpointed VSX Registers
NT_PPC_TM_SPR = 0x10C  # TM Special Purpose Registers
NT_PPC_TM_CTAR = 0x10D  # TM checkpointed Target Address Register
NT_PPC_TM_CPPR = 0x10E  # TM checkpointed Program Priority Register
NT_PPC_TM_CDSCR = 0x10F  # TM checkpointed Data Stream Control Register
NT_PPC_PKEY = 0x110  # Memory Protection Keys registers
NT_386_TLS = 0x200  # i386 TLS slots (struct user_desc)
NT_386_IOPERM = 0x201  # x86 io permission bitmap (1=deny)
NT_X86_XSTATE = 0x202  # x86 extended state using xsave
NT_S390_HIGH_GPRS = 0x300  # s390 upper register halves
NT_S390_TIMER = 0x301  # s390 timer register
NT_S390_TODCMP = 0x302  # s390 TOD clock comparator register
NT_S390_TODPREG = 0x303  # s390 TOD programmable register
NT_S390_CTRS = 0x304  # s390 control registers
NT_S390_PREFIX = 0x305  # s390 prefix register
NT_S390_LAST_BREAK = 0x306  # s390 breaking event address
NT_S390_SYSTEM_CALL = 0x307  # s390 system call restart data
NT_S390_TDB = 0x308  # s390 transaction diagnostic block
NT_S390_VXRS_LOW = 0x309  # s390 vector registers 0-15 upper half
NT_S390_VXRS_HIGH = 0x30A  # s390 vector registers 16-31
NT_S390_GS_CB = 0x30B  # s390 guarded storage registers
NT_S390_GS_BC = 0x30C  # s390 guarded storage broadcast control block
NT_S390_RI_CB = 0x30D  # s390 runtime instrumentation
NT_S390_PV_CPU_DATA = 0x30E  # s390 protvirt cpu dump data
NT_ARM_VFP = 0x400  # ARM VFP/NEON registers
NT_ARM_TLS = 0x401  # ARM TLS register
NT_ARM_HW_BREAK = 0x402  # ARM hardware breakpoint registers
NT_ARM_HW_WATCH = 0x403  # ARM hardware watchpoint registers
NT_ARM_SYSTEM_CALL = 0x404  # ARM system call number
NT_ARM_SVE = 0x405  # ARM Scalable Vector Extension registers
NT_ARM_PAC_MASK = 0x406  # ARM pointer authentication code masks
NT_ARM_PACA_KEYS = 0x407  # ARM pointer authentication address keys
NT_ARM_PACG_KEYS = 0x408  # ARM pointer authentication generic key
NT_ARM_TAGGED_ADDR_CTRL = 0x409  # arm64 tagged address control (prctl())
NT_ARM_PAC_ENABLED_KEYS = 0x40A  # arm64 ptr auth enabled keys (prctl())
NT_ARM_SSVE = 0x40B  # ARM Streaming SVE registers
NT_ARM_ZA = 0x40C  # ARM SME ZA registers
NT_ARM_ZT = 0x40D  # ARM SME ZT registers
NT_ARC_V2 = 0x600  # ARCv2 accumulator/extra registers
NT_VMCOREDD = 0x700  # Vmcore Device Dump Note
NT_MIPS_DSP = 0x800  # MIPS DSP ASE registers
NT_MIPS_FP_MODE = 0x801  # MIPS floating-point mode
NT_MIPS_MSA = 0x802  # MIPS SIMD registers
NT_LOONGARCH_CPUCFG = 0xA00  # LoongArch CPU config registers
NT_LOONGARCH_CSR = 0xA01  # LoongArch control and status registers
NT_LOONGARCH_LSX = 0xA02  # LoongArch Loongson SIMD Extension registers
NT_LOONGARCH_LASX = 0xA03  # LoongArch Loongson Advanced SIMD Extension registers
NT_LOONGARCH_LBT = 0xA04  # LoongArch Loongson Binary Translation registers
NT_LOONGARCH_HW_BREAK = 0xA05  # LoongArch hardware breakpoint registers
NT_LOONGARCH_HW_WATCH = 0xA06  # LoongArch hardware watchpoint registers
NT_GNU_PROPERTY_TYPE_0 = 5  # Note types with note name "GNU"
