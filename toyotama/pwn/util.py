import typing
from struct import pack, unpack


def p8(x: int) -> bytes:
    """Pack 8bit integer"""
    return pack("<B" if x > 0 else "<b", x)


def p16(x: int) -> bytes:
    """Pack 16bit integer"""
    return pack("<H" if x > 0 else "<h", x)


def p32(x: int) -> bytes:
    """Pack 32bit integer"""
    return pack("<I" if x > 0 else "<i", x)


def p64(x: int) -> bytes:
    """Pack 64bit integer"""
    return pack("<Q" if x > 0 else "<q", x)


def u8(x: bytes, sign: bool = False) -> bytes:
    """Unpack 8bit byteseger"""
    assert len(x) <= 1
    return unpack("<b" if sign else "<B", x)[0]


def u16(x: bytes, sign: bool = False) -> bytes:
    """Unpack 16bit byteseger"""
    assert len(x) <= 2
    x += b"\x00" * (-len(x) % 2)
    return unpack("<h" if sign else "<H", x)[0]


def u32(x: bytes, sign: bool = False) -> bytes:
    """Unpack 32bit byteseger"""
    assert len(x) <= 4
    x += b"\x00" * (-len(x) % 4)
    return unpack("<i" if sign else "<I", x)[0]


def u64(x: bytes, sign: bool = False) -> bytes:
    """Unpack 64bit byteseger"""
    assert len(x) <= 8
    x += b"\x00" * (-len(x) % 8)
    return unpack("<q" if sign else "<Q", x)[0]


def fill(length: int, character: typing.AnyStr = b"A") -> typing.AnyStr:
    """Generate b"AAA..." padding

    Args:
        length (int): The length of padding.
        character (str or bytes, optional): The character to fill.
    Returns:
        str or bytes: The string by repeating `character` for `length` times
    """
    return character * length
