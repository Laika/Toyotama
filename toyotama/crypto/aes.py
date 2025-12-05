import json
from collections.abc import Callable
from itertools import pairwise
from logging import getLogger
from pathlib import Path
from random import sample

from toyotama.util.bytes_ import Bytes

logger = getLogger(__name__)


def ecb_chosen_plaintext_attack(
    encrypt_oracle: Callable[[bytes], bool],
    plaintext_space: bytes = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789{}_",
    known_plaintext: bytes = b"",
    block_size: int = 16,
):
    """AES ECB mode chosen plaintext attack

    This function helps solving chosen plaintext attack.

    Args:
        encrypt_oracle (typing.Callable[[bytes], bool]): the encryption oracle.
        plaintext_space (bytes, optional): Defaults to uppercase + lowercase + numbers + "{}_".
        known_plaintext (bytes, optional): Defaults to b"".
        block_size (int, optional): Defaults to 16.
    Returns:
        bytes: The plaintext.
    """

    block_end = block_size * (len(known_plaintext) // (block_size - 2) + 1)
    for _ in range(1, 100):
        # shuffle plaintext_space to reduce complexity
        plaintext_space = Bytes(sample(bytearray(plaintext_space), len(plaintext_space)))

        # get the encrypted block which includes the beginning of FLAG
        logger.info("Getting the encrypted block which includes the beginning of FLAG")

        if len(known_plaintext) % block_size == block_size - 1:
            block_end += block_size

        chosen_plaintext = Bytes(block_end - len(known_plaintext) - 1)
        encrypted_block = encrypt_oracle(chosen_plaintext)
        encrypted_block = encrypted_block[block_end - block_size : block_end]

        # bruteforcing all of the characters in plaintext_space
        logger.info("Bruteforcing all of the characters in plaintext_space")
        for c in plaintext_space:
            payload = b"\x00" * (block_end - len(known_plaintext) - 1) + known_plaintext + bytearray([c])
            enc_block = encrypt_oracle(payload)[block_end - block_size : block_end]
            if encrypted_block == enc_block:
                known_plaintext += bytearray([c])
                break


class ResumeData:
    def __init__(
        self,
        block_index: int = 0,
        inblock_index: int = 15,
        plaintext: Bytes | None = None,
        decrypted_ct_target: bytearray | None = None,
        ct: bytearray | None = None,
    ):
        self.block_index: int = block_index
        self.inblock_index: int = inblock_index
        self.plaintext: Bytes = plaintext or Bytes()
        self.decrypted_ct_target: bytearray = decrypted_ct_target or bytearray()
        self.ct: bytearray = ct or bytearray()

    def save(self, path: Path):
        data = {
            "block_index": self.block_index,
            "inblock_index": self.inblock_index,
            "plaintext": self.plaintext.hex(),
            "decrypted_ct_target": self.decrypted_ct_target.hex(),
            "ct": self.ct.hex(),
        }

        path.write_text(json.dumps(data))
        logger.info("ResumeData: Saved to %s", path)

    @classmethod
    def load(cls, path: Path) -> "ResumeData":
        data = json.loads(path.read_text())

        resume_data = cls()
        resume_data.block_index = data["block_index"]
        resume_data.inblock_index = data["inblock_index"]
        resume_data.plaintext = Bytes.fromhex(data["plaintext"])
        resume_data.decrypted_ct_target = bytearray.fromhex(data["decrypted_ct_target"])
        resume_data.ct = bytearray.fromhex(data["ct"])

        logger.info("ResumeData: Loaded from %s", path)

        return resume_data


class PKCS7PaddingOracleAttack:
    def __init__(
        self,
        padding_oracle: Callable[[bytes], bool] | None = None,
        block_size: int = 16,
        resume: bool = False,
    ):
        self.padding_oracle = padding_oracle
        self.block_size = block_size
        self.resume: bool = resume
        self.resume_data: ResumeData = ResumeData()

        logger.info("Resume: %s", "Enabled" if self.resume else "Disabled")

    def save(self, path: str | Path) -> None:
        path = Path(path)
        if self.resume_data:
            self.resume_data.save(path)

    def load(self, path: str | Path) -> None:
        path = Path(path)
        self.resume_data = ResumeData.load(path)
        self.resume = True

    @staticmethod
    def _xor(a: bytearray, b: bytearray) -> bytearray:
        assert len(a) == len(b)
        return bytearray(x ^ y for x, y in zip(a, b))

    def _make_padding_block(self, n: int) -> bytearray:
        assert 0 <= n <= self.block_size
        return bytearray([n] * n).rjust(self.block_size, b"\0")

    def set_padding_oracle(self, padding_oracle: Callable[[bytes], bool]):
        self.padding_oracle = padding_oracle

    def solve_decrypted_block(self, ct_target: Bytes, resume: bool = False) -> Bytes:
        """
        [     ct     ]   [ ct_target  ]
              |                |
              +--------+       |
                       | [ Decryption ]
                       |       | <- d
                       |       |
                       +-------x (XOR)
                               |
                         [ Plain text ]
        """
        ct = self.resume_data.ct if resume else bytearray([0 for _ in range(self.block_size)])
        decrypted_ct_target = self.resume_data.decrypted_ct_target if resume else bytearray([0 for _ in range(self.block_size)])

        assert self.padding_oracle
        assert len(ct) == len(decrypted_ct_target)

        initial = self.resume_data.inblock_index - 1 if resume and self.resume_data else self.block_size - 1
        for i in range(initial, -1, -1):
            padding = self.block_size - i

            # Bruteforce one byte
            for c in range(0x100):
                ct[i] = c
                if self.padding_oracle(bytes(ct) + ct_target):
                    # Recalculate d
                    decrypted_ct_target = self._xor(ct, self._make_padding_block(padding))

                    if i == 0:
                        break

                    # Recalculate next c
                    ct = self._xor(decrypted_ct_target, self._make_padding_block(padding + 1))
                    self.resume_data.decrypted_ct_target = decrypted_ct_target
                    self.resume_data.ct = ct
                    self.resume_data.inblock_index = i
                    self.save(Path(f"resume_data_{self.resume_data.block_index}-{self.resume_data.inblock_index}.json"))
                    break
            else:
                raise ValueError("Padding Oracle Attack failed.")
        return Bytes(decrypted_ct_target)

    def decryption_attack(self, ciphertext: bytes) -> bytes:
        """Padding oracle decryption attack.
        This function helps solving padding oracle decryption attack.

        Args:
            ciphertext (bytes): A ciphertext.
        Returns:
            bytes: decrypt(ciphertext)
        """
        ciphertext = Bytes(ciphertext)
        ciphertext_block: list[Bytes] = ciphertext.to_block()
        plaintext_block: Bytes = getattr(self.resume_data, "plaintext")
        block_index: int = getattr(self.resume_data, "block_index")

        for i, (ct1, ct2) in enumerate(pairwise(ciphertext_block)):
            if i < block_index:
                continue
            elif i > block_index:
                plaintext_block += ct1 ^ self.solve_decrypted_block(ct2, resume=self.resume and False)
            else:
                plaintext_block += ct1 ^ self.solve_decrypted_block(ct2, resume=self.resume and True)

            logger.info("plaintext: %r", plaintext_block)
            self.resume_data.block_index = i + 1
            self.resume_data.inblock_index = 15
            self.resume_data.plaintext = plaintext_block
            self.resume_data.ct = bytearray([0 for _ in range(self.block_size)])
            self.resume_data.decrypted_ct_target = bytearray([0 for _ in range(self.block_size)])
            if self.resume:
                self.save(Path(f"resume_data_{self.resume_data.block_index}-{self.resume_data.inblock_index}.json"))

        return plaintext_block

    def encryption_attack(self, plaintext: bytes, ciphertext: bytes, iv: bytes) -> tuple[bytes, bytes]:
        """Padding oracle encryption attack.
        This function helps solving padding oracle encryption attack.

        Args:
            plaintext (bytes): A plaintext.
            ciphertext (bytes): A ciphertext.
            iv (bytes): An initialization vector.
        Returns:
            tuple[bytes, bytes]: iv and ciphertext.
        """

        plaintext_block: list[Bytes] = Bytes(plaintext).to_block()
        ciphertext_block: list[Bytes] = Bytes(ciphertext).to_block()
        tampered_ciphertext_block: list[bytes] = [ciphertext_block.pop()]
        while plaintext_block:
            pt, ct = plaintext_block.pop(), tampered_ciphertext_block[0]
            tampered_ciphertext_block = [pt ^ self.solve_decrypted_block(ct)] + tampered_ciphertext_block

        iv = tampered_ciphertext_block.pop(0)
        tampered_ciphertext = b"".join(tampered_ciphertext_block)
        return tampered_ciphertext, iv
