import pytest

from toyotama.crypto.aes import PKCS7PaddingOracleAttack


@pytest.mark.skip(reason="Requires external server on localhost:50000")
def test_padding():
    """Integration test for padding oracle attack.

    This test requires an external server running on localhost:50000.
    Skip by default as it's an integration test.
    """
    from toyotama.connect import Socket

    _r = Socket("nc localhost 50000")

    def oracle(ciphertext: bytes, iv: bytes) -> bool:
        _r.sendlineafter("> ", (iv + ciphertext).hex())
        result = _r.recvline().decode().strip()
        return result == "ok"

    ciphertext = bytes.fromhex(_r.recvline().decode())
    iv = bytes.fromhex(_r.recvline().decode())
    po = PKCS7PaddingOracleAttack()
    po.set_padding_oracle(oracle)

    tampered_plaintext = b"FLAG{Y0u_hav3_succ33ded_1n_tamp3r1n9_padding_oracle_@ttack}\x05\x05\x05\x05\x05"
    assert len(tampered_plaintext) == 64
    tampered_ciphertext, iv = po.encryption_attack(tampered_plaintext, ciphertext, iv)
    _r.sendlineafter(b"> ", (iv + tampered_ciphertext).hex().encode())
    _r.recvline().decode()
    _r.recvline().decode()
