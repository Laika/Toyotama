import logging
from os import getenv

from rich.logging import RichHandler

from .connect import Process, Socket, Tube
from .elf import *  # Keep * for many ELF constants and structs
from .pwn import *  # Keep * for many syscall constants
from .terminal import (
    CustomFormatter, hex_to_ansi_color_code, fg, bg,
    RED, YELLOW, BLUE, GREEN, MAGENTA, CYAN, VIOLET, DEEP_PURPLE, 
    ORANGE, LIGHT_GRAY, GRAY, DARK_GRAY, WHITE, BLACK,
    copy_to_clipboard
)
from .util import (
    BitStream, Bytes, to_block, b64_padding, binary_to_image,
    parse_args, decompress_zip, decompress_bz2, decompress_7z, 
    decompress_tar, get_file_format, decompress, main,
    Int, UInt8, UChar, UInt16, UInt32, UInt64, 
    Int8, Int16, Int32, Int64, execute, Text,
    MarkdownTable, CyclicString, printvall, extract_flag, 
    extract_flag_str, extract_flag_bytes, random_string, de_bruijn
)
from .web import session_falsification

logger = logging.getLogger("toyotama")
logger.setLevel(getenv("TOYOTAMA_LOG_LEVEL", "INFO").upper())
handler = RichHandler(rich_tracebacks=True)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)

from .crypto import (
    ResumeData, PKCS7PaddingOracleAttack, ecb_chosen_plaintext_attack,
    rot, PRIMES, P192, P224, P256, P384, P521, W25519, W448,
    SHA256, LibcRandom, lcg_crack, RSASolver, common_modulus_attack, 
    wieners_attack, lsb_decryption_oracle_attack, int_to_bytes, bytes_to_int, 
    is_prime, miller_rabin_test, next_prime, xor, rotl, rotr, extended_gcd, 
    legendre, mod_sqrt, chinese_remainder, babystep_giantstep, pohlig_hellman, 
    factorize_from_kphi, factorize_from_ed, inverse, is_square, solve_quadratic_equation
)

# SageMath dependent imports (if available)
try:
    from .crypto import shortest_vector, babai_closest_plane, closest_vectors_embedding, closest_vectors
except ImportError:
    pass
