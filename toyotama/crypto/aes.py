import sys
from itertools import pairwise
from random import sample
from typing import Callable

from toyotama.crypto.util import xor
from toyotama.util.connect import Connect
from toyotama.util.log import Logger, Style
from toyotama.util.util import to_block

log = Logger()


def ecb_chosen_plaintext_attack(
    encrypt_oracle: Callable[[bytes], bool],
    plaintext_space: bytes = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789{}_",
    known_plaintext: bytes = b"",
    block_size: int = 16,
    verbose: bool = False,
):
    """AES ECB mode chosen plaintext attack

    This function helps solving chosen plaintext attack.

    Args:
        encrypt_oracle (typing.Callable[[bytes], bool]): the encryption oracle.
        plaintext_space (bytes, optional): Defaults to uppercase + lowercase + numbers + "{}_".
        known_plaintext (bytes, optional): Defaults to b"".
        block_size (int, optional): Defaults to 16.
        verbose (bool, optional): Defaults to False.
    Returns:
        bytes: The plaintext.
    """

    block_end = block_size * (len(known_plaintext) // (block_size - 2) + 1)
    for _ in range(1, 100):

        # shuffle plaintext_space to reduce complexity
        plaintext_space = bytes(sample(bytearray(plaintext_space), len(plaintext_space)))

        # get the encrypted block which includes the beginning of FLAG
        if verbose:
            log.progress("Getting the encrypted block which includes the beginning of FLAG")

        if len(known_plaintext) % block_size == block_size - 1:
            block_end += block_size

        chosen_plaintext = b"\x00" * (block_end - len(known_plaintext) - 1)
        encrypted_block = encrypt_oracle(chosen_plaintext)
        encrypted_block = encrypted_block[block_end - block_size : block_end]

        # bruteforcing all of the characters in plaintext_space
        if verbose:
            log.progress("Bruteforcing all of the characters in plaintext_space")
        for c in plaintext_space:
            if verbose:
                sys.stderr.write(
                    f"\r{log.colored(Style.Color.GREY, known_plaintext[:-1].decode())}"
                    f"{log.colored(Style.Color.RED, known_plaintext[-1:].decode())}"
                    f"{log.colored(Style.MAGENTA, chr(c))}"
                )
            payload = b"\x00" * (block_end - len(known_plaintext) - 1) + known_plaintext + bytearray([c])
            enc_block = encrypt_oracle(payload)[block_end - block_size : block_end]
            if encrypted_block == enc_block:
                known_plaintext += bytearray([c])
                if verbose:
                    sys.stderr.write("\n")
                break


class PKCS7PaddingOracleAttack:
    def __init__(
        self,
        padding_oracle: Callable[[bytes], bool] = None,
        block_size: int = 16,
        debug: bool = False,
    ):
        self.padding_oracle = padding_oracle
        self.block_size = block_size
        self.debug = debug

    @staticmethod
    def _xor(a: bytearray, b: bytearray) -> bytearray:
        assert len(a) == len(b)
        return bytearray([x ^ y for x, y in zip(a, b)])

    def _make_padding_block(self, n: int) -> bytearray:
        assert 0 <= n <= self.block_size
        return bytearray([n] * n).rjust(self.block_size, b"\0")

    def set_padding_oracle(self, padding_oracle: Callable[[bytes], bool]):
        self.padding_oracle = padding_oracle

    def solve_decrypted_block(self, ct_target: bytes) -> bytes:
        """
        [_____ct_____]   [_ct_target__]
              |                |
              +--------+       |
                       | [ Decryption ]
                       |       | <- d
                       |       |
                       +-------x (XOR)
                               |
                         [ Plain text ]
        """
        ct = bytearray([0 for _ in range(self.block_size)])
        d = bytearray([0 for _ in range(self.block_size)])

        for i in range(self.block_size - 1, -1, -1):
            padding = self.block_size - i

            # Bruteforce one byte
            for c in range(0x100):
                ct[i] = c
                if self.padding_oracle(bytes(ct + ct_target)):
                    # Recalculate d
                    d = self._xor(ct, self._make_padding_block(padding))

                    if i == 0:
                        break

                    # Recalculate next c
                    ct = self._xor(d, self._make_padding_block(padding + 1))
                    break
            else:
                raise ValueError("Padding Oracle Attack failed.")
        return d

    def decryption_attack(self, iv: bytes, ciphertext: bytes) -> bytes:
        """Padding oracle decryption attack.
        This function helps solving "Padding Oracle Attack"

        Args:
            iv (bytes, optional): An initialization vector.
            ciphertext (bytes): A ciphertext.
        Returns:
            bytes: decrypt(ciphertext)
        """
        ciphertext_block: list[bytes] = [iv] + to_block(ciphertext)
        plaintext_block = b""

        for ct1, ct2 in pairwise(ciphertext_block):
            plaintext_block += xor(ct1, self.solve_decrypted_block(ct2))

        return plaintext_block

    def encryption_attack():
        ...


def test_padding():
    _r = Connect("nc localhost 50000")

    def oracle(ciphertext: bytes) -> bool:
        _r.sendlineafter(b"> ", ciphertext.hex())
        result = _r.recvline().decode().strip()
        return result == "ok"

    ciphertext = bytes.fromhex(_r.recvline().decode())
    iv = bytes.fromhex(_r.recvline().decode())
    po = PKCS7PaddingOracleAttack()
    po.set_padding_oracle(oracle)
    result = po.decryption_attack(iv, ciphertext)
    print(result)


if __name__ == "__main__":
    test_padding()
