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


def u8(x: int, sign: bool = False) -> bytes:
    """Unpack 8bit integer"""
    return unpack("<B" if x > 0 else "<b", x)[0]


def u16(x: int, sign: bool = False) -> bytes:
    """Unpack 16bit integer"""
    return unpack("<H" if x > 0 else "<h", x)[0]


def u32(x: int, sign: bool = False) -> bytes:
    """Unpack 32bit integer"""
    return unpack("<I" if x > 0 else "<i", x)[0]


def u64(x: int, sign: bool = False) -> bytes:
    """Unpack 64bit integer"""
    return unpack("<Q" if x > 0 else "<q", x)[0]


def fill(length: int, character: typing.AnyStr = b"A") -> typing.AnyStr:
    """Generate b"AAA..." padding

    Args:
        length (int): The length of padding.
        character (str or bytes, optional): The character to fill.
    Returns:
        str or bytes: The string by repeating `character` for `length` times
    """
    return character * length
