import os
from logging import getLogger

from toyotama.crypto.aes import ResumeData, PKCS7PaddingOracleAttack, ecb_chosen_plaintext_attack
from toyotama.crypto.classical_cipher import rot
from toyotama.crypto.const import PRIMES
from toyotama.crypto.curve import P192, P224, P256, P384, P521, W25519, W448
from toyotama.crypto.hash import SHA256
from toyotama.crypto.rng import LibcRandom, lcg_crack
from toyotama.crypto.rsa import RSASolver, common_modulus_attack, wieners_attack, lsb_decryption_oracle_attack
from toyotama.crypto.util import (
    int_to_bytes, bytes_to_int, is_prime, miller_rabin_test, next_prime, 
    xor, rotl, rotr, extended_gcd, legendre, mod_sqrt, chinese_remainder, 
    babystep_giantstep, pohlig_hellman, factorize_from_kphi, factorize_from_ed, 
    inverse, is_square, solve_quadratic_equation
)

try:
    from sage.all import *
    from toyotama.crypto.lattice import shortest_vector, babai_closest_plane, closest_vectors_embedding, closest_vectors
except ImportError:
    logger = getLogger(__name__)
    if not os.environ.get("TOYOTAMA_IGNORE_SAGEMATH", False):
        logger.warning("SageMath is not installed. Some functions may not work.")
