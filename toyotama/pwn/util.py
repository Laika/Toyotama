from struct import pack, unpack

p8   = lambda x: pack('<B' if x > 0 else '<b', x)
p16  = lambda x: pack('<H' if x > 0 else '<h', x)
p32  = lambda x: pack('<I' if x > 0 else '<i', x)
p64  = lambda x: pack('<Q' if x > 0 else '<q', x)
u8   = lambda x, sign=False: unpack('<B' if not sign else '<b', x)[0] 
u16  = lambda x, sign=False: unpack('<H' if not sign else '<h', x)[0] 
u32  = lambda x, sign=False: unpack('<I' if not sign else '<i', x)[0] 
u64  = lambda x, sign=False: unpack('<Q' if not sign else '<q', x)[0] 
fill = lambda x, c='A', byte=True: (c*x).encode() if byte else c*x
